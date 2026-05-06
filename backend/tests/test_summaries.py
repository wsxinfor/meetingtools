"""Integration tests for meeting summary generation and edit."""
import uuid
from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.meeting import Meeting
from app.services.llm.provider import LlmResult
from main import app


@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.fixture
async def meeting_with_text(client: AsyncClient, db: AsyncSession) -> dict:
    resp = await client.post("/api/meetings", json={"title": "纪要生成测试会议"})
    meeting_id = resp.json()["data"]["id"]
    await db.execute(
        Meeting.__table__.update()
        .where(Meeting.id == uuid.UUID(meeting_id))
        .values(corrected_text="这是一段测试转写文本，用于验证纪要生成。")
    )
    await db.commit()
    return {"meeting_id": meeting_id}


@pytest.fixture
async def llm_config_id(client: AsyncClient) -> str:
    resp = await client.post(
        "/api/llm-configs",
        json={
            "name": "测试LLM",
            "provider": "ollama",
            "base_url": "http://localhost:6014/v1",
            "model_name": "test-model",
            "is_default": True,
        },
    )
    yield resp.json()["data"]["id"]
    await client.delete(f"/api/llm-configs/{resp.json()['data']['id']}")


@pytest.mark.asyncio
async def test_generate_summary(
    client: AsyncClient, meeting_with_text: dict, llm_config_id: str
) -> None:
    meeting_id = meeting_with_text["meeting_id"]

    # Get a template ID
    resp = await client.get("/api/templates")
    template_id = resp.json()["data"][0]["id"]

    mock_result = LlmResult(
        content="# 会议摘要\n\n这是测试纪要内容。\n\n# 行动项\n\n- 无",
        model="test-model",
        latency_ms=200,
    )

    with patch("app.services.summary_service.llm_provider.generate", return_value=mock_result):
        resp = await client.post(
            f"/api/meetings/{meeting_id}/summaries",
            json={"template_id": template_id, "llm_config_id": llm_config_id},
        )

    assert resp.status_code == 200
    s = resp.json()["data"]
    summary_id = s["id"]
    assert s["llm_model"] == "test-model"
    assert "会议摘要" in s["content_md"]

    # List summaries
    resp = await client.get(f"/api/meetings/{meeting_id}/summaries")
    assert resp.status_code == 200
    ids = [x["id"] for x in resp.json()["data"]]
    assert summary_id in ids

    # Update summary
    resp = await client.put(
        f"/api/summaries/{summary_id}",
        json={"content_md": "# 修改后的纪要\n\n内容已更新。", "is_final": True},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["is_final"] is True
    assert "修改后的纪要" in resp.json()["data"]["content_md"]


@pytest.mark.asyncio
async def test_generate_summary_no_llm_config(
    client: AsyncClient, meeting_with_text: dict
) -> None:
    meeting_id = meeting_with_text["meeting_id"]
    resp = await client.get("/api/templates")
    template_id = resp.json()["data"][0]["id"]

    resp = await client.post(
        f"/api/meetings/{meeting_id}/summaries",
        json={"template_id": template_id},
    )
    # May succeed (if a default config exists) or fail with 400
    assert resp.status_code in (200, 400)


@pytest.mark.asyncio
async def test_generate_summary_meeting_not_found(client: AsyncClient) -> None:
    resp = await client.post(
        f"/api/meetings/{uuid.uuid4()}/summaries",
        json={"template_id": str(uuid.uuid4())},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_summary_not_found(client: AsyncClient) -> None:
    resp = await client.put(
        f"/api/summaries/{uuid.uuid4()}",
        json={"content_md": "x"},
    )
    assert resp.status_code == 404
