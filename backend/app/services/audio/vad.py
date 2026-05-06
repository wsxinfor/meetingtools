import re
import subprocess
from dataclasses import dataclass


@dataclass
class SpeechSegment:
    start_ms: int
    end_ms: int


_SILENCE_START = re.compile(r"silence_start: ([0-9.]+)")
_SILENCE_END = re.compile(r"silence_end: ([0-9.]+)")


def detect_speech_segments(
    wav_path: str,
    silence_threshold_db: float = -40.0,
    min_silence_ms: int = 300,
    min_segment_ms: int = 500,
    merge_gap_ms: int = 500,
) -> list[SpeechSegment]:
    """Detect speech segments in a WAV file using ffmpeg silencedetect.

    Expects 16kHz mono WAV (output of normalize_audio). Returns segments sorted
    by start time with short gaps merged and sub-threshold segments removed.
    """
    cmd = [
        "ffmpeg", "-i", wav_path,
        "-af", f"silencedetect=noise={silence_threshold_db}dB:d={min_silence_ms / 1000:.3f}",
        "-f", "null", "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    stderr = result.stderr

    # Parse silence intervals from ffmpeg stderr
    silence_starts = [float(m) for m in _SILENCE_START.findall(stderr)]
    silence_ends = [float(m) for m in _SILENCE_END.findall(stderr)]

    # Derive total duration from stderr (last reported time or silence_end)
    duration = _probe_duration(wav_path)

    # Build silence intervals, pairing starts with ends
    silences: list[tuple[float, float]] = []
    for i, s_start in enumerate(silence_starts):
        s_end = silence_ends[i] if i < len(silence_ends) else duration
        silences.append((s_start, s_end))

    # Derive speech intervals as the complement of silence
    speech_intervals: list[tuple[float, float]] = []
    cursor = 0.0
    for s_start, s_end in silences:
        if s_start > cursor:
            speech_intervals.append((cursor, s_start))
        cursor = s_end
    if cursor < duration:
        speech_intervals.append((cursor, duration))

    # Convert to ms
    segments_ms = [(int(s * 1000), int(e * 1000)) for s, e in speech_intervals]

    # Merge segments with small gaps
    merged: list[tuple[int, int]] = []
    for start, end in segments_ms:
        if merged and start - merged[-1][1] <= merge_gap_ms:
            merged[-1] = (merged[-1][0], end)
        else:
            merged.append((start, end))

    # Filter out very short segments
    return [
        SpeechSegment(start_ms=s, end_ms=e)
        for s, e in merged
        if e - s >= min_segment_ms
    ]


def _probe_duration(wav_path: str) -> float:
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "a:0",
        "-show_entries", "stream=duration",
        "-of", "csv=p=0",
        wav_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except ValueError:
        return 0.0
