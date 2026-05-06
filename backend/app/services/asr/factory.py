from app.core.config import settings
from app.services.asr.base import AsrProvider


def get_asr_provider() -> AsrProvider:
    provider = settings.asr_provider.lower()
    if provider == "http":
        from app.services.asr.http_provider import HttpAsrProvider
        return HttpAsrProvider(base_url=settings.asr_http_url)
    # Default: mock (safe for development / tests)
    from app.services.asr.mock_provider import MockAsrProvider
    return MockAsrProvider()
