import asyncio
import gc
import logging
import os
import re
import subprocess
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ASR_MODEL = os.getenv("ASR_MODEL", "iic/SenseVoiceSmall")
SPK_MODEL = os.getenv("SPK_MODEL", "iic/speech_campplus_sv_zh-cn_16k-common")
VAD_MODEL = os.getenv("VAD_MODEL", "fsmn-vad")
PUNC_MODEL = os.getenv("PUNC_MODEL", "ct-punc-c")
ITN_MODEL = os.getenv("ITN_MODEL", "")
CLUSTER_MODEL = os.getenv("CLUSTER_MODEL", "clustering")
DEVICE = os.getenv("DEVICE", "cpu")
NCPU = int(os.getenv("NCPU", "2"))
# Max minutes per chunk for long audio; 0 = no chunking
CHUNK_MINUTES = int(os.getenv("CHUNK_MINUTES", "15"))

_model = None
_ready = False


def _load():
    global _model, _ready
    from funasr import AutoModel  # noqa: PLC0415

    kwargs: dict = dict(
        model=ASR_MODEL,
        device=DEVICE,
        ncpu=NCPU,
        disable_update=True,
        disable_pbar=True,
    )
    if VAD_MODEL:
        kwargs["vad_model"] = VAD_MODEL
    if PUNC_MODEL:
        kwargs["punc_model"] = PUNC_MODEL
    if SPK_MODEL:
        kwargs["spk_model"] = SPK_MODEL
    if ITN_MODEL:
        kwargs["itn_model"] = ITN_MODEL
    logger.info(
        "Loading model %s + vad=%s + punc=%s + spk=%s + itn=%s + cluster=%s on %s (ncpu=%d) ...",
        ASR_MODEL, VAD_MODEL or "(built-in)", PUNC_MODEL or "(built-in)",
        SPK_MODEL or "(none)", ITN_MODEL or "(none)", CLUSTER_MODEL,
        DEVICE, NCPU,
    )
    _model = AutoModel(**kwargs)
    _ready = True
    logger.info("Model ready")


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _load)
    yield


app = FastAPI(title="FunASR HTTP Service", lifespan=lifespan)


_CN_NUMS = "零一二三四五六七八九十"


def _clean(text: str) -> str:
    """Remove SenseVoice special tokens like <|NOTIMESTAMPS|> or <|zh|>."""
    return re.sub(r"<\|[^|]+\|>", "", text).strip()


_FILLER_RE = re.compile(
    r"(?:"
    r"嗯+|啊+|呃+|哦+|噢+|额+|唔+|哼+|诶+|哎+"
    r"|对对对+|嗯嗯+|哦哦+|好好好+|是是是+"
    r"|就是说|然后[，,]|那个[，,]|这个[，,]"
    r"|怎么说呢|其实吧|对吧[，,]?|是吧[，,]?"
    r"|就是[，,]|就是是+|就是就是"
    r"|或者或者+|就是的"
    r")"
)

_PURE_PUNCT_RE = re.compile(r"^[，,。！？；、：""''…—\-\s]+$")


def _remove_fillers(text: str) -> str:
    """Remove Chinese filler words (语气词) from transcript text."""
    text = _FILLER_RE.sub("", text)
    text = re.sub(r"[，,]{2,}", "，", text)
    text = re.sub(r"[。]{2,}", "。", text)
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()


def _is_pure_punct(text: str) -> bool:
    """Check if text contains only punctuation/whitespace."""
    return bool(_PURE_PUNCT_RE.match(text))


def _speaker_label(spk_id: int) -> str:
    if 0 <= spk_id < len(_CN_NUMS):
        return f"发言人{_CN_NUMS[spk_id]}"
    return f"发言人{spk_id}"


def _audio_to_wav(src_path: str, dst_path: str) -> None:
    """Convert any audio to 16kHz mono 16-bit WAV on disk."""
    r = subprocess.run(
        [
            "ffmpeg", "-nostdin", "-i", src_path,
            "-f", "wav", "-acodec", "pcm_s16le",
            "-ac", "1", "-ar", "16000",
            "-y", dst_path,
        ],
        capture_output=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion failed: {r.stderr[-300:]}")


def _split_wav(src_path: str, chunk_sec: int, out_dir: str) -> list[str]:
    """Split a WAV file into chunks of chunk_sec seconds using ffmpeg.

    Uses ffprobe to get total duration first, then extracts exactly the
    needed number of chunks. This avoids the ffmpeg bug where -ss past
    the end of a file still exits with code 0 and produces a tiny
    header-only WAV file.
    """
    total_duration = _get_duration(src_path)
    if total_duration <= 0:
        return [src_path]

    num_chunks = int(total_duration // chunk_sec) + (1 if total_duration % chunk_sec > 0.5 else 0)
    logger.info("Splitting %.1fs into %d chunks of %ds", total_duration, num_chunks, chunk_sec)

    paths: list[str] = []
    for idx in range(num_chunks):
        out_path = os.path.join(out_dir, f"chunk_{idx:04d}.wav")
        r = subprocess.run(
            [
                "ffmpeg", "-nostdin", "-i", src_path,
                "-ss", str(idx * chunk_sec),
                "-t", str(chunk_sec),
                "-f", "wav", "-acodec", "pcm_s16le",
                "-ac", "1", "-ar", "16000",
                "-y", out_path,
            ],
            capture_output=True,
        )
        if r.returncode != 0:
            break
        # Verify the chunk has actual audio content (duration > 0.1s)
        chunk_dur = _get_duration(out_path)
        if chunk_dur < 0.1:
            os.remove(out_path)
            break
        paths.append(out_path)

    return paths


def _get_duration(path: str) -> float:
    r = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True,
    )
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0


def _transcribe_single(wav_path: str, offset_ms: int = 0) -> tuple[str, list[dict]]:
    """Transcribe a single WAV chunk. offset_ms shifts timestamps."""
    import torch  # noqa: PLC0415

    gen_kwargs: dict = dict(
        input=wav_path,
        is_final=True,
        sentence_timestamp=True,
        batch_size_s=300,
    )
    if CLUSTER_MODEL and SPK_MODEL:
        gen_kwargs["cluster_model"] = CLUSTER_MODEL

    with torch.no_grad():
        result = _model.generate(**gen_kwargs)

    if not result:
        return "", []

    full_text = _clean(result[0].get("text", ""))
    sentence_info = result[0].get("sentence_info") or result[0].get("sentences") or []

    segments = []
    for item in sentence_info:
        text = _remove_fillers(_clean(item.get("text", "")))
        if not text or _is_pure_punct(text):
            continue
        spk_id = item.get("spk", 0)
        segments.append({
            "speaker": _speaker_label(spk_id),
            "start_ms": int(item.get("start", 0)) + offset_ms,
            "end_ms": int(item.get("end", 0)) + offset_ms,
            "text": text,
        })

    # Fallback: if no sentence_info, create one segment
    if not segments and full_text:
        segments = [{
            "speaker": "发言人零",
            "start_ms": offset_ms,
            "end_ms": offset_ms,
            "text": _remove_fillers(full_text),
        }]

    return _remove_fillers(full_text), segments


def _transcribe(wav_path: str) -> tuple[str, list[dict]]:
    """Transcribe audio, chunking long files to avoid OOM."""
    duration = _get_duration(wav_path)
    chunk_sec = CHUNK_MINUTES * 60

    # Short audio: process in one go
    if chunk_sec <= 0 or duration <= chunk_sec + 30:
        return _transcribe_single(wav_path)

    # Long audio: split into chunks, process each, then merge
    logger.info("Long audio %.1fs > %ds, splitting into %dmin chunks",
                duration, chunk_sec, CHUNK_MINUTES)

    with tempfile.TemporaryDirectory(prefix="asr_chunks_") as chunk_dir:
        chunk_paths = _split_wav(wav_path, chunk_sec, chunk_dir)
        logger.info("Split into %d chunks", len(chunk_paths))

        all_text_parts: list[str] = []
        all_segments: list[dict] = []

        for i, cp in enumerate(chunk_paths):
            offset_ms = i * chunk_sec * 1000
            logger.info("Processing chunk %d/%d (offset %dms)", i + 1, len(chunk_paths), offset_ms)
            text, segs = _transcribe_single(cp, offset_ms)
            if text:
                all_text_parts.append(text)
            all_segments.extend(segs)
            # Free memory between chunks
            gc.collect()

    full_text = "".join(all_text_parts)
    return full_text, all_segments


@app.get("/health")
def health():
    if not _ready:
        raise HTTPException(status_code=503, detail="model loading")
    return {"status": "ok"}


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    if not _ready:
        raise HTTPException(status_code=503, detail="model not ready")

    suffix = Path(file.filename or "audio").suffix or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        while chunk := await file.read(1024 * 1024):
            tmp.write(chunk)
        tmp_path = tmp.name

    wav_path = tmp_path + ".wav"
    try:
        duration = _get_duration(tmp_path)
        logger.info("Received audio %.1fs", duration)

        _audio_to_wav(tmp_path, wav_path)
        wav_size = os.path.getsize(wav_path)
        logger.info("Converted to WAV: %d bytes", wav_size)

        loop = asyncio.get_event_loop()
        full_text, segments = await loop.run_in_executor(None, _transcribe, wav_path)

        logger.info("Done: %d segments, %d chars", len(segments), len(full_text))
        return {"text": full_text, "segments": segments, "confidence": 1.0}
    except Exception as exc:
        logger.error("Transcription error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        Path(tmp_path).unlink(missing_ok=True)
        Path(wav_path).unlink(missing_ok=True)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6013, log_level="info")
