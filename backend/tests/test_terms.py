"""Integration tests for term dictionary and apply-terms."""
import uuid

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting import Meeting
from main import app


@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_term_crud(client: AsyncClient) -> None:
    # Create
    resp = await client.post(
        "/api/terms",
        json={"wrong_text": "A I", "correct_text": "AI", "category": "brand"},
    )
    assert resp.status_code == 200
    term_id = resp.json()["data"]["id"]
    assert resp.json()["data"]["wrong_text"] == "A I"

    # List
    resp = await client.get("/api/terms")
    assert resp.status_code == 200
    ids = [t["id"] for t in resp.json()["data"]]
    assert term_id in ids

    # Update
    resp = await client.put(f"/api/terms/{term_id}", json={"correct_text": "AI技术", "enabled": True})
    assert resp.status_code == 200
    assert resp.json()["data"]["correct_text"] == "AI技术"

    # Delete
    resp = await client.delete(f"/api/terms/{term_id}")
    assert resp.status_code == 200

    resp = await client.get("/api/terms")
    ids = [t["id"] for t in resp.json()["data"]]
    assert term_id not in ids


@pytest.mark.asyncio
async def test_apply_terms(client: AsyncClient, db: AsyncSession) -> None:
    # Create a term
    await client.post("/api/terms", json={"wrong_text": "错误词", "correct_text": "正确词"})

    # Create a meeting with raw_text containing the wrong word
    resp = await client.post("/api/meetings", json={"title": "纠错测试会议"})
    meeting_id = resp.json()["data"]["id"]

    await db.execute(
        Meeting.__table__.update()
        .where(Meeting.id == uuid.UUID(meeting_id))
        .values(raw_text="这里有一个错误词，需要纠正。")
    )
    await db.commit()

    # Apply terms
    resp = await client.post(f"/api/meetings/{meeting_id}/apply-terms")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert "正确词" in data["corrected_text"]
    assert "错误词" not in data["corrected_text"]

    # Verify meeting corrected_text updated
    resp = await client.get(f"/api/meetings/{meeting_id}")
    assert "正确词" in resp.json()["data"]["corrected_text"]


@pytest.mark.asyncio
async def test_apply_terms_with_aliases(client: AsyncClient, db: AsyncSession) -> None:
    await client.post(
        "/api/terms",
        json={"wrong_text": "WRONG", "correct_text": "RIGHT", "aliases": ["Wrng", "wrng"]},
    )
    resp = await client.post("/api/meetings", json={"title": "别名纠错测试"})
    meeting_id = resp.json()["data"]["id"]

    await db.execute(
        Meeting.__table__.update()
        .where(Meeting.id == uuid.UUID(meeting_id))
        .values(raw_text="WRONG and Wrng and wrng")
    )
    await db.commit()

    resp = await client.post(f"/api/meetings/{meeting_id}/apply-terms")
    assert resp.status_code == 200
    assert resp.json()["data"]["corrected_text"] == "RIGHT and RIGHT and RIGHT"


@pytest.mark.asyncio
async def test_term_not_found(client: AsyncClient) -> None:
    resp = await client.put(f"/api/terms/{uuid.uuid4()}", json={"enabled": False})
    assert resp.status_code == 404

    resp = await client.delete(f"/api/terms/{uuid.uuid4()}")
    assert resp.status_code == 404
