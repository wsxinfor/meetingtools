import pytest
from httpx import ASGITransport, AsyncClient

from main import app


@pytest.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_create_and_list_customer(client: AsyncClient) -> None:
    resp = await client.post("/api/customers", json={"name": "测试客户", "industry": "IT"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["code"] == 0
    customer_id = data["data"]["id"]

    resp = await client.get("/api/customers")
    assert resp.status_code == 200
    ids = [c["id"] for c in resp.json()["data"]]
    assert customer_id in ids


@pytest.mark.asyncio
async def test_create_project(client: AsyncClient) -> None:
    resp = await client.post("/api/customers", json={"name": "客户A"})
    customer_id = resp.json()["data"]["id"]

    resp = await client.post(
        "/api/projects", json={"customer_id": customer_id, "name": "项目X", "stage": "立项"}
    )
    assert resp.status_code == 200
    assert resp.json()["code"] == 0


@pytest.mark.asyncio
async def test_save_corrected_text(client: AsyncClient) -> None:
    resp = await client.post("/api/meetings", json={"title": "纠错文本测试"})
    meeting_id = resp.json()["data"]["id"]

    resp = await client.put(
        f"/api/meetings/{meeting_id}/corrected-text",
        json={"corrected_text": "经过纠错的完整会议记录文本"},
    )
    assert resp.status_code == 200
    assert resp.json()["data"]["corrected_text"] == "经过纠错的完整会议记录文本"

    resp = await client.get(f"/api/meetings/{meeting_id}")
    assert resp.json()["data"]["corrected_text"] == "经过纠错的完整会议记录文本"


@pytest.mark.asyncio
async def test_meeting_crud(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/meetings",
        json={"title": "售前交流会", "meeting_type": "presales", "participants": ["张三", "李四"]},
    )
    assert resp.status_code == 200
    meeting_id = resp.json()["data"]["id"]

    resp = await client.get(f"/api/meetings/{meeting_id}")
    assert resp.status_code == 200
    assert resp.json()["data"]["title"] == "售前交流会"

    resp = await client.put(f"/api/meetings/{meeting_id}", json={"title": "售前交流会（更新）"})
    assert resp.status_code == 200
    assert resp.json()["data"]["title"] == "售前交流会（更新）"

    resp = await client.get("/api/meetings?page=1&page_size=20")
    assert resp.status_code == 200
    assert resp.json()["data"]["total"] >= 1

    resp = await client.delete(f"/api/meetings/{meeting_id}")
    assert resp.status_code == 200

    resp = await client.get(f"/api/meetings/{meeting_id}")
    assert resp.status_code == 404
