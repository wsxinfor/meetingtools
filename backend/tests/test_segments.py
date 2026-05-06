"""Integration tests for transcript segment API."""
import io
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.audio.vad import SpeechSegment
from app.services.segment_service import create_segments_from_vad
from main import app


@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def meeting_with_segments(client: AsyncClient, db: AsyncSession) -> dict:
    resp = await client.post("/api/meetings", json={"title": "片段测试会议"})
    assert resp.status_code == 200
    meeting_id = resp.json()["data"]["id"]

    fake_segments = [
        SpeechSegment(start_ms=0, end_ms=2000),
        SpeechSegment(start_ms=3000, end_ms=6000),
    ]
    with (
        patch("app.services.audio_service._preprocess_task", new_callable=AsyncMock),
    ):
        resp = await client.post(
            f"/api/meetings/{meeting_id}/audio",
            files={"file": ("s.wav", io.BytesIO(b"RIFF" + b"\x00" * 40), "audio/wav")},
        )
    assert resp.status_code == 200
    audio_file_id = resp.json()["data"]["id"]

    # Directly insert segments via the service (bypass background task in tests)
    await create_segments_from_vad(
        db,
        uuid.UUID(meeting_id),
        uuid.UUID(audio_file_id),
        fake_segments,
    )

    return {"meeting_id": meeting_id, "audio_file_id": audio_file_id}


@pytest.mark.asyncio
async def test_list_segments(client: AsyncClient, meeting_with_segments: dict) -> None:
    meeting_id = meeting_with_segments["meeting_id"]
    resp = await client.get(f"/api/meetings/{meeting_id}/transcript-segments")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) == 2
    assert data[0]["segment_index"] == 0
    assert data[0]["start_ms"] == 0
    assert data[0]["end_ms"] == 2000
    assert data[1]["segment_index"] == 1
    assert data[1]["start_ms"] == 3000


@pytest.mark.asyncio
async def test_update_segment(client: AsyncClient, meeting_with_segments: dict) -> None:
    meeting_id = meeting_with_segments["meeting_id"]
    resp = await client.get(f"/api/meetings/{meeting_id}/transcript-segments")
    segment_id = resp.json()["data"][0]["id"]

    resp = await client.put(
        f"/api/transcript-segments/{segment_id}",
        json={"corrected_text": "修正文本", "speaker_label": "张总"},
    )
    assert resp.status_code == 200
    result = resp.json()["data"]
    assert result["corrected_text"] == "修正文本"
    assert result["speaker_label"] == "张总"


@pytest.mark.asyncio
async def test_list_segments_meeting_not_found(client: AsyncClient) -> None:
    import uuid
    fake_id = str(uuid.uuid4())
    resp = await client.get(f"/api/meetings/{fake_id}/transcript-segments")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_segment_not_found(client: AsyncClient) -> None:
    import uuid
    resp = await client.put(
        f"/api/transcript-segments/{uuid.uuid4()}",
        json={"corrected_text": "x"},
    )
    assert resp.status_code == 404
