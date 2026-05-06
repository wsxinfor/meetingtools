# 测试规范

## 1. 测试目录结构

```
backend/
  tests/
    unit/                  # 纯函数、工具类、service 层单元测试
      services/
        test_audio_service.py
        test_term_correction.py
      utils/
        test_prompt_builder.py
    integration/           # API endpoint 端到端集成测试（真实 DB）
      test_meetings.py
      test_audio.py
      test_transcripts.py
      test_summaries.py
    fixtures/              # 测试用静态文件
      sample.wav           # ≤ 1 MB 的测试音频
      sample_transcript.json
    conftest.py            # 全局 fixture：测试 DB、app client
```

---

## 2. 后端测试策略

### 2.1 单元测试（unit）

**测试对象：** services 层中的纯函数，不依赖 DB 或外部服务的逻辑。

```python
# tests/unit/services/test_term_correction.py
from app.services.term_correction import apply_corrections

def test_apply_corrections_replaces_known_term():
    terms = [{"wrong": "AI助理", "correct": "AI 助手"}]
    result = apply_corrections("会议中AI助理发言", terms)
    assert result == "会议中AI 助手发言"

def test_apply_corrections_case_insensitive():
    ...
```

### 2.2 集成测试（integration）

**测试对象：** FastAPI endpoint，使用真实 PostgreSQL 测试库。

**核心约定：**
- **禁止 mock 数据库**，测试依赖真实 DB（测试库，非生产库）
- 允许 mock 外部服务：ASR（FunASR）、LLM（Ollama/vLLM）
- 每个 endpoint 至少覆盖 happy path + 404/422 等常见错误路径

```python
# tests/integration/test_meetings.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_meeting(client: AsyncClient, db_meeting_fixture):
    response = await client.post("/api/v1/meetings", json={
        "title": "产品评审",
        "customer_id": db_meeting_fixture.customer_id,
        "project_id": db_meeting_fixture.project_id,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 0
    assert data["data"]["title"] == "产品评审"

@pytest.mark.asyncio
async def test_get_meeting_not_found(client: AsyncClient):
    response = await client.get("/api/v1/meetings/99999")
    assert response.status_code == 404
```

### 2.3 conftest.py 示例

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import app
from app.db.base import Base
from app.core.config import settings

TEST_DATABASE_URL = settings.test_database_url  # 从环境变量读取测试 DB

@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
```

### 2.4 Mock 外部服务

```python
# 正确：mock ASR 服务，不 mock DB
@pytest.mark.asyncio
async def test_trigger_asr(client, mocker):
    mocker.patch("app.services.asr.funasr_provider.transcribe", return_value=[
        {"start": 0.0, "end": 3.5, "text": "测试文本"}
    ])
    response = await client.post("/api/v1/audio/1/asr")
    assert response.status_code == 200
```

---

## 3. 覆盖率要求

| 层次 | 目标覆盖率 | 说明 |
|------|-----------|------|
| services 层 | ≥ 70% | 核心业务逻辑必须覆盖 |
| API endpoints | 100% happy path | 每个 endpoint 至少一个成功测试 |
| models/schemas | 不做强制要求 | Pydantic/SQLAlchemy 声明性代码 |
| workers | ≥ 50% | 任务调度逻辑 |

运行覆盖率：

```bash
pytest --cov=app --cov-report=html tests/
```

---

## 4. 前端测试策略（V1）

V1 阶段前端测试以轻量为主，不强制 E2E。

**测试工具：** Vitest（单元）

**测试对象：**
- Pinia store 的状态变更逻辑
- `src/utils/` 下的纯函数（格式化、日期处理等）
- API 响应数据转换函数

**E2E：** V1 暂不强制，靠手动验收覆盖主流程。

```typescript
// src/stores/__tests__/useMeetingStore.test.ts
import { setActivePinia, createPinia } from 'pinia'
import { useMeetingStore } from '../useMeetingStore'
import { vi } from 'vitest'

describe('useMeetingStore', () => {
  beforeEach(() => setActivePinia(createPinia()))

  it('sets loading state during fetch', async () => {
    const store = useMeetingStore()
    vi.spyOn(store, 'fetchMeetings').mockResolvedValue([])
    await store.fetchMeetings()
    expect(store.loading).toBe(false)
  })
})
```

---

## 5. 测试数据管理

- 静态 fixture 文件放 `backend/tests/fixtures/`
- 测试音频文件大小 **≤ 1 MB**（使用裁剪后的小样本）
- 数据库 fixture 使用 pytest fixture 函数动态创建，不用 SQL dump 文件
- 每个测试用例后自动回滚（使用事务 fixture 或 `scope="function"` 隔离）

---

## 6. 运行命令

```bash
# 运行全部测试
pytest

# 只跑单元测试
pytest tests/unit/

# 只跑集成测试
pytest tests/integration/

# 带覆盖率报告
pytest --cov=app --cov-report=term-missing tests/

# 快速验证单个文件
pytest tests/integration/test_meetings.py -v
```
