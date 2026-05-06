"""Unit tests for normalize_audio — requires ffmpeg on PATH."""
import os
import struct
import tempfile
from pathlib import Path

import pytest

from app.services.audio.preprocess import AudioMeta, normalize_audio


def _make_wav(path: str, sample_rate: int = 44100, duration_s: float = 0.5) -> None:
    num_samples = int(sample_rate * duration_s)
    data_size = num_samples * 2  # 16-bit mono
    with open(path, "wb") as f:
        f.write(b"RIFF")
        f.write(struct.pack("<I", 36 + data_size))
        f.write(b"WAVE")
        f.write(b"fmt ")
        f.write(struct.pack("<IHHIIHH", 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
        f.write(b"data")
        f.write(struct.pack("<I", data_size))
        f.write(b"\x00" * data_size)


@pytest.mark.skipif(
    os.system("ffmpeg -version > /dev/null 2>&1") != 0,
    reason="ffmpeg not available",
)
def test_normalize_audio_produces_16k_mono() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "input.wav")
        dst = os.path.join(tmp, "output.wav")
        _make_wav(src, sample_rate=44100, duration_s=1.0)

        meta = normalize_audio(src, dst)

        assert Path(dst).exists()
        assert meta.sample_rate == 16000
        assert meta.channels == 1
        assert meta.duration_seconds > 0


@pytest.mark.skipif(
    os.system("ffmpeg -version > /dev/null 2>&1") != 0,
    reason="ffmpeg not available",
)
def test_normalize_audio_bad_input_raises() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "bad.wav")
        Path(src).write_bytes(b"notaudiodata")
        dst = os.path.join(tmp, "out.wav")

        with pytest.raises(RuntimeError):
            normalize_audio(src, dst)
