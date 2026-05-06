"""Integration tests for ASR task API."""
import io
import uuid
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audio import AudioFile
from main import app


@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def meeting_and_audio(client: AsyncClient, db: AsyncSession) -> dict:
    resp = await client.post("/api/meetings", json={"title": "ASR测试会议"})
    assert resp.status_code == 200
    meeting_id = resp.json()["data"]["id"]

    with patch("app.services.audio_service._preprocess_task", new_callable=AsyncMock):
        resp = await client.post(
            f"/api/meetings/{meeting_id}/audio",
            files={"file": ("test.wav", io.BytesIO(b"RIFF" + b"\x00" * 40), "audio/wav")},
        )
    assert resp.status_code == 200
    audio_file_id = resp.json()["data"]["id"]

    # Mark audio as preprocessed so ASR task will accept it
    await db.execute(
        AudioFile.__table__.update()
        .where(AudioFile.id == uuid.UUID(audio_file_id))
        .values(status="preprocessed", normalized_path="/tmp/fake_norm.wav")
    )
    await db.commit()

    return {"meeting_id": meeting_id, "audio_file_id": audio_file_id}


@pytest.mark.asyncio
async def test_start_asr_task(client: AsyncClient, meeting_and_audio: dict) -> None:
    meeting_id = meeting_and_audio["meeting_id"]
    audio_file_id = meeting_and_audio["audio_file_id"]

    with patch("app.services.asr_task_service._run_asr_bg", new_callable=AsyncMock):
        resp = await client.post(
            f"/api/meetings/{meeting_id}/asr-tasks",
            json={"audio_file_id": audio_file_id, "engine": "mock"},
        )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "pending"
    assert data["engine"] == "mock"
    assert data["meeting_id"] == meeting_id


@pytest.mark.asyncio
async def test_get_asr_task(client: AsyncClient, meeting_and_audio: dict) -> None:
    meeting_id = meeting_and_audio["meeting_id"]
    audio_file_id = meeting_and_audio["audio_file_id"]

    with patch("app.services.asr_task_service._run_asr_bg", new_callable=AsyncMock):
        resp = await client.post(
            f"/api/meetings/{meeting_id}/asr-tasks",
            json={"audio_file_id": audio_file_id, "engine": "mock"},
        )
    task_id = resp.json()["data"]["id"]

    resp = await client.get(f"/api/asr-tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == task_id


@pytest.mark.asyncio
async def test_asr_task_meeting_not_found(client: AsyncClient) -> None:
    import uuid
    resp = await client.post(
        f"/api/meetings/{uuid.uuid4()}/asr-tasks",
        json={"audio_file_id": str(uuid.uuid4()), "engine": "mock"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_asr_task_not_found(client: AsyncClient) -> None:
    import uuid
    resp = await client.get(f"/api/asr-tasks/{uuid.uuid4()}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_mock_provider_produces_text() -> None:
    from app.services.asr.mock_provider import MockAsrProvider
    provider = MockAsrProvider()
    result = provider.transcribe_file("/tmp/some_clip.wav")
    assert isinstance(result.text, str)
    assert len(result.text) > 0
