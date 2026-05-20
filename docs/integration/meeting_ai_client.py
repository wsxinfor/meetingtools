"""
meeting-ai → local-asr-service integration example.

Usage:
    pip install requests
    ASR_BASE_URL=http://your-server:18080/api \
    ASR_API_KEY=asr_xxxxxxxxxxxx \
    python meeting_ai_client.py meeting.mp3
"""

import os
import sys
import time
import json
import requests

# ── Configuration ──────────────────────────────────────────────────────────────
BASE_URL = os.environ.get("ASR_BASE_URL", "http://localhost:18080/api")
API_KEY  = os.environ.get("ASR_API_KEY", "asr_your_key_here")

HEADERS = {"Authorization": f"Bearer {API_KEY}"}

POLL_INTERVAL_S  = 5    # seconds between status checks
POLL_TIMEOUT_S   = 3600 # give up after 1 hour
TERMINAL_STATUSES = {"done", "failed", "cancelled"}


# ── Step 1: Upload audio and create task ───────────────────────────────────────
def upload_audio(
    file_path: str,
    *,
    language: str = "zh",
    enable_diarization: bool = False,
    enable_filler_removal: bool = False,
    hotword_set_id: str | None = None,
) -> dict:
    """
    Upload an audio file and return the task info.
    Returns: {"task_id": "uuid", "status": "queued"}
    """
    with open(file_path, "rb") as f:
        form = {
            "language": (None, language),
            "enable_vad": (None, "true"),
            "enable_punctuation": (None, "true"),
            "enable_diarization": (None, str(enable_diarization).lower()),
            "enable_filler_removal": (None, str(enable_filler_removal).lower()),
        }
        if hotword_set_id:
            form["hotword_set_id"] = (None, hotword_set_id)

        resp = requests.post(
            f"{BASE_URL}/v1/transcriptions",
            headers=HEADERS,
            files={"file": (os.path.basename(file_path), f)},
            data={k: v[1] for k, v in form.items()},
            timeout=120,
        )

    resp.raise_for_status()
    return resp.json()["data"]


# ── Step 2: Poll until done ────────────────────────────────────────────────────
def poll_until_done(task_id: str) -> dict:
    """
    Poll /v1/transcriptions/{task_id} until the task reaches a terminal state.
    Returns the final status dict.
    Raises TimeoutError if it takes too long.
    Raises RuntimeError if the task fails.
    """
    deadline = time.time() + POLL_TIMEOUT_S
    while time.time() < deadline:
        resp = requests.get(
            f"{BASE_URL}/v1/transcriptions/{task_id}",
            headers=HEADERS,
            timeout=10,
        )
        resp.raise_for_status()
        status = resp.json()["data"]

        print(
            f"  [{status['status']}] progress={status['progress']}%"
            + (f"  error: {status['error_message']}" if status.get("error_message") else ""),
            flush=True,
        )

        if status["status"] in TERMINAL_STATUSES:
            if status["status"] == "failed":
                raise RuntimeError(f"ASR task failed: {status.get('error_message')}")
            if status["status"] == "cancelled":
                raise RuntimeError("ASR task was cancelled")
            return status

        time.sleep(POLL_INTERVAL_S)

    raise TimeoutError(f"ASR task {task_id} did not complete within {POLL_TIMEOUT_S}s")


# ── Step 3: Fetch structured result ───────────────────────────────────────────
def fetch_result(task_id: str) -> dict:
    """
    Fetch the full transcription result after the task is done.

    Returns dict with shape:
    {
        "task_id": str,
        "engine":  str,
        "duration_seconds": float | None,
        "full_text": str,
        "segments": [
            {
                "index":      int,     # zero-based segment index
                "start_ms":   int,     # segment start in milliseconds
                "end_ms":     int,     # segment end in milliseconds
                "speaker_id": str | None,  # e.g. "SPEAKER_00" when diarization is on
                "text":       str,     # recognized + post-processed text
                "confidence": float | None
            },
            ...
        ]
    }
    """
    resp = requests.get(
        f"{BASE_URL}/v1/transcriptions/{task_id}/result",
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["data"]


# ── Step 4: Download export file (optional) ────────────────────────────────────
def download_export(task_id: str, fmt: str, dest_path: str) -> None:
    """
    Download a formatted export file.
    fmt: one of "json", "txt", "srt", "vtt"
    """
    resp = requests.get(
        f"{BASE_URL}/v1/transcriptions/{task_id}/download",
        headers=HEADERS,
        params={"format": fmt},
        timeout=30,
        stream=True,
    )
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"  Saved {fmt.upper()} → {dest_path}")


# ── Helper: convert result to meeting-ai transcript_segments format ────────────
def to_transcript_segments(result: dict) -> list[dict]:
    """
    Map the ASR result into the shape meeting-ai uses for transcript_segments.
    Adjust field names to match your own schema.
    """
    return [
        {
            "sequence":   seg["index"],
            "start_ms":   seg["start_ms"],
            "end_ms":     seg["end_ms"],
            "speaker":    seg["speaker_id"],  # None when diarization is off
            "text":       seg["text"],
            "confidence": seg["confidence"],
            "source":     "local-asr",
        }
        for seg in result["segments"]
    ]


# ── Main demo ──────────────────────────────────────────────────────────────────
def transcribe(file_path: str, **upload_kwargs) -> list[dict]:
    """
    Full pipeline: upload → poll → fetch result → return transcript_segments.
    """
    print(f"Uploading: {file_path}")
    task = upload_audio(file_path, **upload_kwargs)
    task_id = task["task_id"]
    print(f"Task created: {task_id}")

    print("Polling for completion...")
    poll_until_done(task_id)

    print("Fetching result...")
    result = fetch_result(task_id)
    print(f"  Duration: {result['duration_seconds']:.1f}s  |  Segments: {len(result['segments'])}")
    print(f"  Full text preview: {result['full_text'][:120]}...")

    segments = to_transcript_segments(result)
    return segments


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python meeting_ai_client.py <audio_file> [--diarization]")
        sys.exit(1)

    audio_file = sys.argv[1]
    use_diarization = "--diarization" in sys.argv

    segments = transcribe(audio_file, enable_diarization=use_diarization)
    print("\n=== transcript_segments (first 3) ===")
    print(json.dumps(segments[:3], ensure_ascii=False, indent=2))
