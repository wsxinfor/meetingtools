# 代码规范

## 1. Python 后端

### 命名约定

| 类型 | 风格 | 示例 |
|------|------|------|
| 模块/文件 | snake_case | `audio_service.py` |
| 类 | PascalCase | `AsrProvider` |
| 函数/变量 | snake_case | `get_meeting_by_id` |
| 常量 | UPPER_SNAKE | `MAX_FILE_SIZE_MB` |
| 私有方法 | `_` 前缀 | `_build_prompt` |

### 类型注解

- 所有函数参数和返回值**必须**标注类型
- 使用 `from __future__ import annotations` 避免循环引用
- 复杂类型用 `TypeAlias` 命名（Python 3.10+）

```python
# 正确
async def create_meeting(data: MeetingCreate) -> MeetingRead:
    ...

# 错误
async def create_meeting(data):
    ...
```

### 格式化

- **Black**：行宽 88，`pyproject.toml` 中配置 `[tool.black] line-length = 88`
- **isort**：`profile = "black"`，与 Black 兼容
- 提交前运行：`black . && isort .`

### 异常处理

```python
# 正确：捕获具体类型
try:
    result = await asr_service.transcribe(path)
except FileNotFoundError as e:
    raise HTTPException(status_code=404, detail="音频文件不存在") from e
except ASRTimeoutError as e:
    raise HTTPException(status_code=503, detail="ASR 服务超时") from e

# 错误：裸 except 或 Exception 兜底
try:
    ...
except:          # 禁止
    pass
except Exception:  # 禁止（除非是顶层全局兜底）
    pass
```

### 日志

```python
import logging
logger = logging.getLogger(__name__)

# 正确
logger.info("ASR task started", extra={"task_id": task_id, "meeting_id": meeting_id})
logger.error("ASR failed: %s", str(e), exc_info=True)

# 错误
print("ASR task started")    # 禁止
logger.info(f"音频路径: {audio_path}")  # 禁止记录完整文件路径到 INFO 级
```

### SQLAlchemy Async 规范

```python
# 正确：使用 async session，通过依赖注入传入
async def get_meeting(db: AsyncSession, meeting_id: int) -> Meeting | None:
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    return result.scalar_one_or_none()

# 错误：在 service 内部创建 session
async def get_meeting(meeting_id: int):
    async with AsyncSession(engine) as db:   # 禁止在 service 层自建 session
        ...
```

---

## 2. API 规范

### 统一响应格式

```python
# 成功
{"code": 0, "data": {...}, "msg": "ok"}

# 业务错误（通过 HTTPException）
# HTTP 400/404/409/500
{"detail": "具体错误描述"}
```

在 `app/schemas/response.py` 中定义：

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar("T")

class ApiResponse(BaseModel, Generic[T]):
    code: int = 0
    data: T
    msg: str = "ok"
```

### HTTP 状态码约定

| 场景 | 状态码 |
|------|--------|
| 创建成功 | 201 |
| 查询/更新成功 | 200 |
| 资源不存在 | 404 |
| 参数校验失败 | 422（FastAPI 默认） |
| 业务逻辑冲突 | 409 |
| 外部服务失败（ASR/LLM） | 503 |

### 分页格式

```
GET /api/meetings?page=1&page_size=20

响应 data：
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20
}
```

### Router 组织

```
app/api/
  v1/
    meetings.py      # /api/v1/meetings
    audio.py         # /api/v1/audio
    transcripts.py   # /api/v1/transcripts
    terms.py         # /api/v1/terms
    templates.py     # /api/v1/templates
    summaries.py     # /api/v1/summaries
    exports.py       # /api/v1/exports
```

---

## 3. Vue / TypeScript 前端

### 命名约定

| 类型 | 风格 | 示例 |
|------|------|------|
| 组件文件 | PascalCase | `MeetingCard.vue` |
| Composable | `use` 前缀 | `useMeetingList.ts` |
| Pinia store | `use<Domain>Store.ts` | `useMeetingStore.ts` |
| API 模块 | camelCase | `meetingApi.ts` |
| 类型/接口 | PascalCase | `MeetingDetail` |

### 类型安全

```typescript
// 正确
interface ApiResponse<T> {
  code: number
  data: T
  msg: string
}

// 错误：禁止 any
function handleResponse(data: any) { ... }     // 禁止
const result: any = await fetchMeeting(id)     // 禁止
```

### API 层隔离

```typescript
// src/api/meeting.ts
export const meetingApi = {
  list: (params: MeetingListParams) => request.get<MeetingListResponse>('/meetings', { params }),
  create: (data: MeetingCreate) => request.post<MeetingDetail>('/meetings', data),
  get: (id: number) => request.get<MeetingDetail>(`/meetings/${id}`),
}

// 组件中
import { meetingApi } from '@/api/meeting'
// 禁止在组件里直接使用 axios
```

### 组件规范

- `<script setup lang="ts">` 优先（Composition API）
- Props 用 `defineProps<{...}>()` 标注类型
- 异步数据加载放在 Composable，不在 `onMounted` 中直接写业务逻辑

### 样式编码规范

> 完整视觉规范见 `docs/UI_DESIGN.md`

- 所有颜色、字号、间距、圆角必须使用 `frontend/src/styles/tokens.css` 中定义的 CSS 自定义属性（如 `var(--color-primary)`），禁止在 `<style>` 中直接写十六进制色值或硬编码 px 数值
- Element Plus 组件覆盖样式通过 CSS 变量覆盖，禁止直接修改 `el-*` 内部类
- 禁止 `linear-gradient`、`radial-gradient`
- 禁止 `backdrop-filter: blur`（毛玻璃效果）
- 禁止 `box-shadow` 扩散半径 > 8px
- 禁止 `font-weight: 600` 及以上（仅允许 400 / 500）
- 禁止 `border-radius` > 12px
- 禁止 `transition` 时长 > 300ms
- 禁止深色背景或深色主题（本项目仅浅色模式）

---

## 4. Git 规范

### 提交信息格式

```
type(scope): 简短描述（中文或英文均可）

可选：详细说明
```

| type | 场景 |
|------|------|
| `feat` | 新功能 |
| `fix` | Bug 修复 |
| `refactor` | 重构（不改功能） |
| `test` | 增加/修改测试 |
| `docs` | 文档变更 |
| `chore` | 构建/依赖/CI |
| `task` | 按任务文件推进 |

示例：
```
task(asr): 封装 FunASR AsrProvider，支持本地调用
feat(meeting): 新增会议列表分页查询
fix(audio): 修复 ffmpeg 转码超时未清理临时文件
```

### 分支命名

```
feat/<功能简述>
fix/<bug简述>
task/<阶段号>-<阶段名>   # 如 task/05-asr
```
