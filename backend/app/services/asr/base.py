from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class AsrResult:
    text: str
    confidence: float | None = None
    # Per-segment timestamps if the provider returns them
    segments: list[dict] = field(default_factory=list)


class AsrProvider(ABC):
    @abstractmethod
    def transcribe_file(self, audio_path: str) -> AsrResult:
        """Transcribe an audio file synchronously. Call via asyncio.to_thread."""
        ...
