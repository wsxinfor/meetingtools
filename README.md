# local-meeting-ai-kit-v2

本包用于启动“本地会议记录AI工具”的ClaudeCode开发。

## 内容

1. `docs/PRD.md`：会议记录系统PRD
2. `docs/DATA_API_DESIGN.md`：数据结构 + API设计
3. `docs/CODING_STANDARDS.md`：代码规范（Python + Vue/TS + Git）
4. `docs/TESTING_STANDARDS.md`：测试规范（单元/集成/覆盖率要求）
5. `CLAUDE.md`：ClaudeCode项目控制文件（含端口分配）
6. `TASK.md`：任务看板（含进度状态）
7. `tasks/`：分阶段任务文件（00–11）
8. `prompts/`：会议纪要/纠错Prompt模板
9. `audio_pipeline/`：音频处理链路设计
10. `api_design/API_LIST.md`：API清单速览
11. `deploy/ASR_DEPLOYMENT.md`：FunASR部署说明

## 使用方式

将本包解压到项目根目录，使用ClaudeCode时先让它阅读：

1. `CLAUDE.md`
2. `docs/PRD.md`
3. `docs/DATA_API_DESIGN.md`
4. `TASK.md`

然后按 `tasks/` 目录中的任务逐个执行。

## 重要原则

- V1先跑通上传录音生成会议纪要
- FunASR开发阶段可装在开发机，正式阶段部署在服务器
- 不要把Prompt硬编码在代码里
- 不要前端直接调用ASR模型
