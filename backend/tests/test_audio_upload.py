import io
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def meeting_id(client: AsyncClient) -> str:
    resp = await client.post("/api/meetings", json={"title": "音频测试会议"})
    assert resp.status_code == 200
    return resp.json()["data"]["id"]


@pytest.mark.asyncio
async def test_upload_audio_happy_path(client: AsyncClient, meeting_id: str) -> None:
    fake_wav = b"RIFF" + b"\x00" * 40
    with patch("app.services.audio_service._preprocess_task", new_callable=AsyncMock):
        resp = await client.post(
            f"/api/meetings/{meeting_id}/audio",
            files={"file": ("test.wav", io.BytesIO(fake_wav), "audio/wav")},
        )
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["status"] == "uploaded"
    assert data["original_filename"] == "test.wav"
    assert data["file_size"] == len(fake_wav)

    audio_id = data["id"]
    resp2 = await client.get(f"/api/audio-files/{audio_id}")
    assert resp2.status_code == 200
    assert resp2.json()["data"]["id"] == audio_id


@pytest.mark.asyncio
async def test_upload_unsupported_format(client: AsyncClient, meeting_id: str) -> None:
    resp = await client.post(
        f"/api/meetings/{meeting_id}/audio",
        files={"file": ("test.mp4", io.BytesIO(b"fake"), "video/mp4")},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_upload_meeting_not_found(client: AsyncClient) -> None:
    import uuid
    fake_id = str(uuid.uuid4())
    resp = await client.post(
        f"/api/meetings/{fake_id}/audio",
        files={"file": ("test.wav", io.BytesIO(b"RIFF"), "audio/wav")},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_audio_files(client: AsyncClient, meeting_id: str) -> None:
    with patch("app.services.audio_service._preprocess_task", new_callable=AsyncMock):
        for name in ("a.wav", "b.mp3"):
            await client.post(
                f"/api/meetings/{meeting_id}/audio",
                files={"file": (name, io.BytesIO(b"data"), "audio/wav")},
            )
    resp = await client.get(f"/api/meetings/{meeting_id}/audio-files")
    assert resp.status_code == 200
    assert len(resp.json()["data"]) >= 2
