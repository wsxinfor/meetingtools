# CLAUDE.md - 本地会议记录AI工具项目控制文件

## 1. 项目目标

开发一个本地私有化会议记录AI工具，支持PC/手机录音、音频上传、本地ASR识别、术语纠错、模板化会议纪要生成、Word/Markdown导出。

核心原则：

- 音频文件不得上传外部平台；会议文本经用户明确配置后可发送至外部 LLM
- 优先实现V1最小可用版本
- 不做过度设计
- 所有功能围绕“会议记录可用、可改、可导出、可沉淀”

## 2. 技术栈约束

推荐：

- 前端：Vue 3 + TypeScript + Element Plus
- 后端：Python FastAPI
- ORM：SQLAlchemy 2.x async
- 数据库：PostgreSQL 15
- 音频处理：ffmpeg
- ASR：FunASR / SenseVoiceSmall
- LLM：本地 Ollama 或外部 OpenAI 兼容服务，统一通过 `openai` Python SDK 调用，配置存数据库
- 导出：python-docx
- 部署：Docker Compose

## 2.1 端口分配（固定，不得随意更改）

| 服务 | 宿主机端口 | 说明 |
|------|-----------|------|
| 前端（Vite/Nginx） | **6010** | 浏览器访问入口 |
| 后端（FastAPI） | **6011** | API 服务 |
| PostgreSQL | **6012** | 数据库 |
| FunASR | **6013** | ASR 识别服务 |
| Ollama/LLM | **6014** | 本地大模型服务 |
| MinIO（预留） | **6015** | 文件存储，暂不启用 |

> 本项目端口范围：6010–6015。禁止占用此范围外的端口，也禁止与其他项目冲突。

## 3. 开发原则

1. 先完成后端核心链路，再做复杂前端体验
2. 所有长任务必须异步化或任务化
3. ASR调用必须封装，不允许散落在业务代码中
4. 模板Prompt必须存数据库，不要硬编码
5. 术语库必须可维护
6. 每个任务完成后更新相关文档
7. 不要一次性实现实时字幕、TTS、语音克隆、多模型融合

## 4. ASR部署原则

开发阶段：

- 可以在开发机器安装 FunASR 进行调试
- 可以用本地命令或Python库方式调用

正式阶段：

- FunASR必须部署在服务器或独立容器中
- FastAPI通过统一的AsrProvider调用
- 前端永远不直接调用ASR模型

## 5. 项目目录建议

```text
backend/
  app/
    api/
    core/
    models/
    schemas/
    services/
      audio/
      asr/
      llm/
      export/
    workers/
frontend/
  src/
    views/
    components/
    api/
    stores/
    styles/
docs/
prompts/
tasks/
deploy/
```

## 6. 执行方式

ClaudeCode应按 TASK.md 顺序执行，每次只处理一个阶段任务。

执行一个任务前：

1. 阅读 PRD
2. 阅读 DATA_API_DESIGN
3. 阅读当前 task 文件
4. 明确本任务输入/输出
5. 实现后补充测试与文档

## 7. 禁止事项

- 禁止直接把音频上传到公有云ASR
- 禁止前端直接访问模型
- 禁止把Prompt写死在代码里
- 禁止绕过数据库直接散乱保存业务数据
- 禁止V1引入复杂多租户/权限体系
- 禁止在组件内硬编码颜色、字号、间距；必须使用 `frontend/src/styles/tokens.css` 中的 CSS 变量

## 8. 代码规范（摘要）

> 完整规范见 `docs/CODING_STANDARDS.md`

**Python 后端：**

- 全量 type hints，函数参数和返回值均需标注
- 格式化工具：Black（行宽 88）+ isort（profile=black）
- 禁止裸 `except:`，必须捕获具体异常类型
- 禁止用 `print`，统一使用 `logging` 模块
- 不记录音频路径以外的敏感业务内容到 INFO 级以上日志

**FastAPI API 规范：**

- 所有成功响应统一格式：`{"code": 0, "data": ..., "msg": "ok"}`
- 业务错误通过 `HTTPException(status_code=..., detail=...)` 抛出
- 分页统一使用 `page`/`page_size` 查询参数，响应含 `total`
- Router 按业务模块拆分，禁止所有路由堆在一个文件

**Vue / TypeScript 前端：**

- 组件文件名 PascalCase，Composable 以 `use` 开头
- 禁止使用 `any` 类型，用 `unknown` + 类型收窄代替
- API 调用集中在 `src/api/` 层，组件不直接调用 axios
- Pinia store 文件名格式：`use<Domain>Store.ts`

## 9. 测试规范（摘要）

> 完整规范见 `docs/TESTING_STANDARDS.md`

- 后端测试目录：`backend/tests/`，文件命名 `test_*.py`
- 每个 API endpoint 必须有集成测试覆盖 happy path
- **禁止 mock 数据库**，测试使用独立 PostgreSQL 测试库
- 允许 mock 外部服务（ASR、LLM）
- services 层单元测试覆盖率目标 ≥ 70%
- 测试用音频 fixture 文件放 `backend/tests/fixtures/`，大小 ≤ 1 MB

## 10. 任务进度

任务看板维护在 `TASK.md`，按阶段顺序推进，每次只处理一个阶段。
完成某阶段后，将 `TASK.md` 对应行状态更新为 `✅ 已完成`。

## 11. 前端UI设计规范

> 完整规范见 `docs/UI_DESIGN.md`，前端开发必须遵守。

设计定调：简洁、严肃、专业；参考中国明代工笔画与官窑瓷器配色，克制典雅。

**核心禁止项：**
渐变背景、毛玻璃效果、高饱和色、大阴影（扩散半径 > 8px）、粗体（font-weight ≥ 600）、圆角 > 12px、过渡动画 > 300ms、深色主题。

**CSS Design Tokens：**
所有设计变量（颜色、字号、间距、圆角）集中定义在 `frontend/src/styles/tokens.css`。
组件样式必须通过 `var(--...)` 引用这些变量，禁止硬编码任何色值或尺寸数值。

