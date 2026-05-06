import logging

import httpx

from app.services.asr.base import AsrProvider, AsrResult

logger = logging.getLogger(__name__)


class HttpAsrProvider(AsrProvider):
    """Calls a remote ASR service via HTTP.

    Expects the service to expose:
      POST {base_url}/transcribe
      Content-Type: multipart/form-data  (field name: "file")
      Response: {"text": "..."}
    """

    def __init__(self, base_url: str, timeout: float = 120.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def transcribe_file(self, audio_path: str) -> AsrResult:
        with open(audio_path, "rb") as f:
            try:
                resp = httpx.post(
                    f"{self._base_url}/transcribe",
                    files={"file": f},
                    timeout=self._timeout,
                )
                resp.raise_for_status()
                body = resp.json()
                return AsrResult(
                    text=body.get("text", ""),
                    confidence=body.get("confidence"),
                    segments=body.get("segments", []),
                )
            except httpx.HTTPError as exc:
                logger.error("ASR HTTP request failed: %s", exc)
                raise RuntimeError(f"ASR service error: {exc}") from exc
