"""Integration tests for LLM config CRUD and set-default."""
import uuid
from unittest.mock import patch, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture(scope="session")
async def client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_llm_config_crud(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/llm-configs",
        json={
            "name": "本地Ollama",
            "provider": "ollama",
            "base_url": "http://localhost:6014/v1",
            "api_key": "ollama",
            "model_name": "qwen2.5:7b",
            "is_default": False,
        },
    )
    assert resp.status_code == 200
    cfg = resp.json()["data"]
    cfg_id = cfg["id"]
    assert cfg["name"] == "本地Ollama"
    assert cfg["is_default"] is False

    # List
    resp = await client.get("/api/llm-configs")
    assert resp.status_code == 200
    ids = [c["id"] for c in resp.json()["data"]]
    assert cfg_id in ids

    # Update
    resp = await client.put(f"/api/llm-configs/{cfg_id}", json={"model_name": "qwen2.5:14b"})
    assert resp.status_code == 200
    assert resp.json()["data"]["model_name"] == "qwen2.5:14b"

    # Set default
    resp = await client.put(f"/api/llm-configs/{cfg_id}/set-default")
    assert resp.status_code == 200
    assert resp.json()["data"]["is_default"] is True

    # Delete
    resp = await client.delete(f"/api/llm-configs/{cfg_id}")
    assert resp.status_code == 200

    resp = await client.get("/api/llm-configs")
    ids = [c["id"] for c in resp.json()["data"]]
    assert cfg_id not in ids


@pytest.mark.asyncio
async def test_llm_config_not_found(client: AsyncClient) -> None:
    fake = uuid.uuid4()
    resp = await client.put(f"/api/llm-configs/{fake}", json={"model_name": "x"})
    assert resp.status_code == 404

    resp = await client.delete(f"/api/llm-configs/{fake}")
    assert resp.status_code == 404

    resp = await client.put(f"/api/llm-configs/{fake}/set-default")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_llm_config_test_endpoint_failure(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/llm-configs",
        json={
            "name": "测试失败配置",
            "provider": "ollama",
            "base_url": "http://127.0.0.1:19999/v1",
            "model_name": "nonexistent",
        },
    )
    cfg_id = resp.json()["data"]["id"]

    resp = await client.post(f"/api/llm-configs/{cfg_id}/test")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["success"] is False

    await client.delete(f"/api/llm-configs/{cfg_id}")


@pytest.mark.asyncio
async def test_llm_config_test_endpoint_success(client: AsyncClient) -> None:
    from app.services.llm.provider import LlmResult

    resp = await client.post(
        "/api/llm-configs",
        json={
            "name": "模拟成功配置",
            "provider": "ollama",
            "base_url": "http://localhost:6014/v1",
            "model_name": "mock-model",
        },
    )
    cfg_id = resp.json()["data"]["id"]

    mock_result = LlmResult(content="你好，我是测试模型。", model="mock-model", latency_ms=100)
    with patch("app.api.llm_configs.llm_provider.test_connection", return_value=mock_result):
        resp = await client.post(f"/api/llm-configs/{cfg_id}/test")

    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data["success"] is True
    assert data["latency_ms"] == 100

    await client.delete(f"/api/llm-configs/{cfg_id}")
