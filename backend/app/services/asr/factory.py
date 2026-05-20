from __future__ import annotations

from typing import TYPE_CHECKING

from app.core.config import settings
from app.services.asr.base import AsrProvider

if TYPE_CHECKING:
    from app.models.asr_config import AsrConfig


def get_asr_provider(engine: str = "local", asr_config: AsrConfig | None = None) -> AsrProvider:
    if engine == "remote" and asr_config is not None:
        from app.services.asr.remote_provider import RemoteAsrProvider

        return RemoteAsrProvider(
            base_url=asr_config.base_url,
            api_key=asr_config.api_key,
            enable_diarization=asr_config.enable_diarization,
            enable_filler_removal=asr_config.enable_filler_removal,
        )
    if engine in ("http", "local", "funasr"):
        from app.services.asr.http_provider import HttpAsrProvider

        return HttpAsrProvider(base_url=settings.asr_http_url)
    from app.services.asr.mock_provider import MockAsrProvider

    return MockAsrProvider()
