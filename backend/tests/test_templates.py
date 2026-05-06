"""Integration tests for meeting template CRUD API."""
import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_list_templates_includes_defaults(client: AsyncClient) -> None:
    resp = await client.get("/api/templates")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert isinstance(data, list)
    names = [t["name"] for t in data]
    assert "通用会议纪要" in names
    assert "售前客户交流" in names
    assert "项目推进会议" in names
    assert "技术方案讨论" in names
    assert "招投标沟通" in names


@pytest.mark.asyncio
async def test_template_crud(client: AsyncClient) -> None:
    # Create
    resp = await client.post(
        "/api/templates",
        json={
            "name": "测试模板",
            "type": "general",
            "description": "用于测试",
            "prompt_text": "请生成会议纪要。\n\n{{transcript_text}}",
        },
    )
    assert resp.status_code == 200
    t = resp.json()["data"]
    template_id = t["id"]
    assert t["name"] == "测试模板"
    assert t["enabled"] is True

    # Get by ID
    resp = await client.get(f"/api/templates/{template_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["id"] == template_id

    # Update
    resp = await client.put(
        f"/api/templates/{template_id}",
        json={"name": "测试模板已更新", "enabled": False},
    )
    assert resp.status_code == 200
    updated = resp.json()["data"]
    assert updated["name"] == "测试模板已更新"
    assert updated["enabled"] is False

    # List - new template present
    resp = await client.get("/api/templates")
    ids = [t["id"] for t in resp.json()["data"]]
    assert template_id in ids

    # Delete
    resp = await client.delete(f"/api/templates/{template_id}")
    assert resp.status_code == 200

    # Confirm deleted
    resp = await client.get(f"/api/templates/{template_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_template_not_found(client: AsyncClient) -> None:
    fake_id = uuid.uuid4()
    resp = await client.get(f"/api/templates/{fake_id}")
    assert resp.status_code == 404

    resp = await client.put(f"/api/templates/{fake_id}", json={"enabled": False})
    assert resp.status_code == 404

    resp = await client.delete(f"/api/templates/{fake_id}")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_template_validation(client: AsyncClient) -> None:
    # Empty name should fail
    resp = await client.post(
        "/api/templates",
        json={"name": "  ", "prompt_text": "some prompt {{transcript_text}}"},
    )
    assert resp.status_code == 422

    # Empty prompt_text should fail
    resp = await client.post(
        "/api/templates",
        json={"name": "Valid Name", "prompt_text": ""},
    )
    assert resp.status_code == 422
