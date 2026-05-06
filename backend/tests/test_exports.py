"""Integration tests for transcript and summary export."""
import io
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting import Meeting
from app.models.summary import MeetingSummary
from main import app


@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def meeting_id(client: AsyncClient, db: AsyncSession) -> str:
    resp = await client.post("/api/meetings", json={"title": "导出测试会议", "participants": ["张三", "李四"]})
    mid = resp.json()["data"]["id"]
    await db.execute(
        Meeting.__table__.update()
        .where(Meeting.id == uuid.UUID(mid))
        .values(corrected_text="测试转写内容，用于导出验证。")
    )
    await db.commit()
    return mid


@pytest.mark.asyncio
async def test_export_transcript_md(client: AsyncClient, meeting_id: str) -> None:
    resp = await client.post(
        f"/api/meetings/{meeting_id}/export-transcript",
        json={"format": "md"},
    )
    assert resp.status_code == 200
    record = resp.json()["data"]
    export_id = record["id"]
    assert record["file_format"] == "md"
    assert record["export_type"] == "transcript"

    # Download
    resp = await client.get(f"/api/export-records/{export_id}/download")
    assert resp.status_code == 200
    assert b"#" in resp.content


@pytest.mark.asyncio
async def test_export_transcript_docx(client: AsyncClient, meeting_id: str) -> None:
    resp = await client.post(
        f"/api/meetings/{meeting_id}/export-transcript",
        json={"format": "docx"},
    )
    assert resp.status_code == 200
    record = resp.json()["data"]
    export_id = record["id"]
    assert record["file_format"] == "docx"

    resp = await client.get(f"/api/export-records/{export_id}/download")
    assert resp.status_code == 200
    # docx files start with PK (ZIP magic bytes)
    assert resp.content[:2] == b"PK"


@pytest.mark.asyncio
async def test_export_transcript_invalid_format(client: AsyncClient, meeting_id: str) -> None:
    resp = await client.post(
        f"/api/meetings/{meeting_id}/export-transcript",
        json={"format": "pdf"},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_export_summary_md(client: AsyncClient, db: AsyncSession, meeting_id: str) -> None:
    # Insert a summary directly
    summary = MeetingSummary(
        meeting_id=uuid.UUID(meeting_id),
        title="测试纪要",
        content_md="# 会议摘要\n\n测试纪要内容。",
        llm_model="test-model",
        version=1,
        is_final=False,
    )
    db.add(summary)
    await db.commit()
    await db.refresh(summary)

    resp = await client.post(
        f"/api/summaries/{summary.id}/export",
        json={"format": "md"},
    )
    assert resp.status_code == 200
    record = resp.json()["data"]
    export_id = record["id"]

    resp = await client.get(f"/api/export-records/{export_id}/download")
    assert resp.status_code == 200
    assert "会议摘要" in resp.text


@pytest.mark.asyncio
async def test_export_summary_docx(client: AsyncClient, db: AsyncSession, meeting_id: str) -> None:
    summary = MeetingSummary(
        meeting_id=uuid.UUID(meeting_id),
        title="docx纪要",
        content_md="# 标题\n\n内容。\n\n## 行动项\n\n- 事项一",
        llm_model="test-model",
        version=1,
        is_final=False,
    )
    db.add(summary)
    await db.commit()
    await db.refresh(summary)

    resp = await client.post(f"/api/summaries/{summary.id}/export", json={"format": "docx"})
    assert resp.status_code == 200
    export_id = resp.json()["data"]["id"]

    resp = await client.get(f"/api/export-records/{export_id}/download")
    assert resp.status_code == 200
    assert resp.content[:2] == b"PK"


@pytest.mark.asyncio
async def test_download_not_found(client: AsyncClient) -> None:
    resp = await client.get(f"/api/export-records/{uuid.uuid4()}/download")
    assert resp.status_code == 404
