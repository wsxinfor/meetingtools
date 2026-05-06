import asyncio
import logging
import os
import re
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

ASR_MODEL = os.getenv("ASR_MODEL", "iic/SenseVoiceSmall")
SPK_MODEL = os.getenv("SPK_MODEL", "cam++")
DEVICE = os.getenv("DEVICE", "cpu")
NCPU = int(os.getenv("NCPU", "4"))

_model = None
_ready = False


def _load():
    global _model, _ready
    from funasr import AutoModel  # noqa: PLC0415

    logger.info(
        "Loading model %s + spk_model %s on %s (ncpu=%d) ...",
        ASR_MODEL, SPK_MODEL, DEVICE, NCPU,
    )
    _model = AutoModel(
        model=ASR_MODEL,
        spk_model=SPK_MODEL,
        device=DEVICE,
        ncpu=NCPU,
        disable_update=True,
    )
    _ready = True
    logger.info("Model ready")


@asynccontextmanager
async def lifespan(app: FastAPI):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _load)
    yield


app = FastAPI(title="FunASR HTTP Service", lifespan=lifespan)


def _clean(text: str) -> str:
    return re.sub(r"<\|[^|]+\|>", "", text).strip()


def _parse_segments(raw: list[dict]) -> list[dict]:
    """Convert FunASR sentence_info list to our segment format."""
    segments = []
    for item in raw:
        text = _clean(item.get("text", ""))
        if not text:
            continue
        spk_id = item.get("spk", 0)
        segments.append({
            "speaker": f"spk{spk_id}",
            "start_ms": int(item.get("start", 0)),
            "end_ms": int(item.get("end", 0)),
            "text": text,
        })
    return segments


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
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        result = _model.generate(
            input=tmp_path,
            language="auto",
            use_itn=True,
            batch_size_s=300,
            sentence_timestamp=True,
        )
        if not result:
            return {"text": "", "segments": [], "confidence": 1.0}

        full_text = _clean(result[0].get("text", ""))

        # sentence_info is populated when spk_model is active
        sentence_info = result[0].get("sentence_info") or result[0].get("sentences") or []
        segments = _parse_segments(sentence_info)

        return {"text": full_text, "segments": segments, "confidence": 1.0}
    except Exception as exc:
        logger.error("Transcription error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        Path(tmp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=6013, log_level="info")
