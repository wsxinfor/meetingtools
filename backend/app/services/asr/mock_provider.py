import os

from app.services.asr.base import AsrProvider, AsrResult


class MockAsrProvider(AsrProvider):
    """Returns deterministic placeholder text. Used in tests and when no ASR service is configured."""

    def transcribe_file(self, audio_path: str) -> AsrResult:
        filename = os.path.basename(audio_path)
        return AsrResult(text=f"[模拟识别结果: {filename}]", confidence=1.0)
