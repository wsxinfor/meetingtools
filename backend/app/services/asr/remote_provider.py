import logging
import time

import httpx

from app.services.asr.base import AsrProvider, AsrResult

logger = logging.getLogger(__name__)

_POLL_INTERVAL = 5
_POLL_TIMEOUT = 3600
_UPLOAD_TIMEOUT = 120
_STATUS_TIMEOUT = 10
_RESULT_TIMEOUT = 30


class RemoteAsrProvider(AsrProvider):
    """Calls a remote ASR service using async polling.

    Protocol:
      1. POST /v1/transcriptions  — upload audio, get task_id
      2. GET  /v1/transcriptions/{task_id}  — poll until done/failed
      3. GET  /v1/transcriptions/{task_id}/result  — fetch segments
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        enable_diarization: bool = True,
        enable_filler_removal: bool = True,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._enable_diarization = enable_diarization
        self._enable_filler_removal = enable_filler_removal

    def _headers(self) -> dict[str, str]:
        h = {}
        if self._api_key:
            h["Authorization"] = f"Bearer {self._api_key}"
        return h

    def transcribe_file(self, audio_path: str) -> AsrResult:
        task_id = self._submit(audio_path)
        logger.info("Remote ASR task submitted: %s", task_id)
        self._poll(task_id)
        return self._fetch_result(task_id)

    def _submit(self, audio_path: str) -> str:
        with open(audio_path, "rb") as f:
            resp = httpx.post(
                f"{self._base_url}/v1/transcriptions",
                files={"file": f},
                data={
                    "enable_diarization": str(self._enable_diarization).lower(),
                    "enable_filler_removal": str(self._enable_filler_removal).lower(),
                },
                headers=self._headers(),
                timeout=_UPLOAD_TIMEOUT,
            )
        resp.raise_for_status()
        body = resp.json()
        task_id = body["data"]["task_id"]
        return task_id

    def _poll(self, task_id: str) -> None:
        start = time.monotonic()
        while time.monotonic() - start < _POLL_TIMEOUT:
            resp = httpx.get(
                f"{self._base_url}/v1/transcriptions/{task_id}",
                headers=self._headers(),
                timeout=_STATUS_TIMEOUT,
            )
            resp.raise_for_status()
            body = resp.json()
            status = body["data"]["status"]
            progress = body["data"].get("progress", 0)
            logger.info("Remote ASR task %s: status=%s progress=%d%%", task_id, status, progress)

            if status == "done":
                return
            if status == "failed":
                error = body["data"].get("error_message", "未知错误")
                raise RuntimeError(f"远程ASR失败: {error}")
            if status == "cancelled":
                raise RuntimeError("远程ASR任务被取消")

            time.sleep(_POLL_INTERVAL)

        raise RuntimeError(f"远程ASR超时（{_POLL_TIMEOUT}秒）")

    def _fetch_result(self, task_id: str) -> AsrResult:
        resp = httpx.get(
            f"{self._base_url}/v1/transcriptions/{task_id}/result",
            headers=self._headers(),
            timeout=_RESULT_TIMEOUT,
        )
        resp.raise_for_status()
        body = resp.json()
        data = body["data"]

        segments = []
        for seg in data.get("segments", []):
            segments.append({
                "start_ms": seg["start_ms"],
                "end_ms": seg["end_ms"],
                "text": seg["text"],
                "speaker": seg.get("speaker_id"),
            })

        return AsrResult(
            text=data.get("full_text", ""),
            confidence=None,
            segments=segments,
        )
