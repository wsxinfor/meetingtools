import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AudioMeta:
    duration_seconds: float
    sample_rate: int
    channels: int


def normalize_audio(input_path: str, output_path: str) -> AudioMeta:
    """Convert audio to 16kHz mono WAV with loudnorm, return metadata."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ac", "1",
        "-ar", "16000",
        "-af", "loudnorm",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        logger.error("ffmpeg stderr: %s", result.stderr)
        raise RuntimeError(f"ffmpeg failed (exit {result.returncode}): {result.stderr[-500:]}")

    meta = _probe(output_path)
    logger.info("Normalized audio saved: %s (%.1fs)", output_path, meta.duration_seconds)
    return meta


def _probe(path: str) -> AudioMeta:
    """Extract duration/sample_rate/channels via ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=duration,sample_rate,channels",
        "-of", "csv=p=0",
        path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr}")
    # ffprobe csv output order: sample_rate,channels,duration
    parts = result.stdout.strip().split(",")
    return AudioMeta(
        sample_rate=int(float(parts[0])) if parts[0] else 16000,
        channels=int(float(parts[1])) if len(parts) > 1 else 1,
        duration_seconds=float(parts[2]) if len(parts) > 2 else 0.0,
    )
