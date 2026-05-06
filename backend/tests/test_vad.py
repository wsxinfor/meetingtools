"""Unit tests for VAD (voice activity detection) using ffmpeg silencedetect."""
import struct
import wave
from pathlib import Path

import pytest

from app.services.audio.vad import SpeechSegment, detect_speech_segments


def _make_wav(path: Path, duration_s: float, sample_rate: int = 16000) -> None:
    """Write a minimal sine-like WAV with silence at start and end."""
    n_samples = int(duration_s * sample_rate)
    # 0.5s silence, speech in middle, 0.5s silence
    silence_samples = int(0.5 * sample_rate)
    speech_samples = n_samples - 2 * silence_samples

    silence = b"\x00\x00" * silence_samples
    # Simple non-zero "speech" signal (square wave at -10dB approx)
    amplitude = 8000
    speech = b"".join(struct.pack("<h", amplitude if i % 2 == 0 else -amplitude)
                      for i in range(speech_samples))

    with wave.open(str(path), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(silence + speech + silence)


@pytest.fixture(scope="module")
def wav_with_speech(tmp_path_factory: pytest.TempPathFactory) -> Path:
    p = tmp_path_factory.mktemp("vad") / "test_speech.wav"
    _make_wav(p, duration_s=3.0)
    return p


@pytest.fixture(scope="module")
def silent_wav(tmp_path_factory: pytest.TempPathFactory) -> Path:
    p = tmp_path_factory.mktemp("vad") / "test_silent.wav"
    with wave.open(str(p), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(b"\x00\x00" * 16000)  # 1s pure silence
    return p


def test_detect_speech_returns_segments(wav_with_speech: Path) -> None:
    segments = detect_speech_segments(str(wav_with_speech))
    assert isinstance(segments, list)
    assert len(segments) >= 1
    for seg in segments:
        assert isinstance(seg, SpeechSegment)
        assert seg.start_ms >= 0
        assert seg.end_ms > seg.start_ms


def test_detect_speech_silent_audio_returns_empty(silent_wav: Path) -> None:
    segments = detect_speech_segments(str(silent_wav))
    assert segments == []


def test_detect_speech_segment_bounds(wav_with_speech: Path) -> None:
    segments = detect_speech_segments(str(wav_with_speech))
    for seg in segments:
        assert seg.end_ms - seg.start_ms >= 500, "segments shorter than min_segment_ms should be filtered"
