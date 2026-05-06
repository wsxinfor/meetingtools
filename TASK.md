# TASK.md - 任务看板

> 状态说明：⬜ 待开始 / 🔄 进行中 / ✅ 已完成 / ⏸ 阻塞
>
> 每次只处理一个阶段任务。完成后将状态更新为 ✅，再开始下一阶段。

| # | 阶段 | 目标 | 对应文件 | 状态 | 依赖 |
|---|------|------|----------|------|------|
| 0 | 项目初始化 | 建立前后端基础工程、数据库、Docker开发环境 | `tasks/00-project-init.md` | ✅ 已完成 | — |
| 1 | 会议基础管理 | 实现客户、项目、会议的基础CRUD | `tasks/01-meeting-management.md` | ✅ 已完成 | #0 |
| 2 | 音频上传与文件管理 | 支持会议上传音频，保存文件元数据 | `tasks/02-audio-upload.md` | ✅ 已完成 | #1 |
| 3 | 音频预处理 | 使用ffmpeg统一音频格式，生成标准wav | `tasks/03-audio-preprocess.md` | ✅ 已完成 | #2 |
| 4 | VAD切分与片段管理 | 对音频进行语音片段检测，保存时间戳片段 | `tasks/04-vad-segmentation.md` | ✅ 已完成 | #3 |
| 5 | ASR识别模块 | 封装FunASR识别能力，生成转写片段文本 | `tasks/05-asr-funasr.md` | ✅ 已完成 | #4 |
| 6 | 转写编辑页面/API | 支持查看、编辑、保存转写片段和完整文本 | `tasks/06-transcript-editor.md` | ✅ 已完成 | #5 |
| 7 | 术语库与自动纠错 | 实现术语库维护和会议文本纠错 | `tasks/07-term-correction.md` | ✅ 已完成 | #6 |
| 8 | 模板管理 | 实现会议纪要Prompt模板的增删改查 | `tasks/08-template-management.md` | ✅ 已完成 | #6 |
| 9 | 会议纪要生成 | 调用本地LLM按模板生成纪要 | `tasks/09-summary-generation.md` | ✅ 已完成 | #7 #8 |
| 10 | Word/Markdown导出 | 导出原始转写和会议纪要 | `tasks/10-export.md` | ✅ 已完成 | #9 |
| 11 | 前端整合与验收 | 完成V1页面闭环和验收测试 | `tasks/11-frontend-integration.md` | ✅ 已完成 | #10 |

---

## 执行流程

每开始一个阶段：

1. 将状态改为 `🔄 进行中`
2. 阅读 `docs/PRD.md` + `docs/DATA_API_DESIGN.md` + 对应 task 文件
3. 按 CLAUDE.md 代码规范和测试规范实现
4. 完成后补写集成测试，确认 API happy path 通过
5. 将状态改为 `✅ 已完成`，再推进下一阶段
