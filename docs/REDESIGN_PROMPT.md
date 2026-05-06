# REDESIGN_PROMPT.md — 交给 Claude Code 的启动指令

将以下内容复制粘贴给 Claude Code 作为第一条指令：

---

请先阅读以下文件，然后按照 FRONTEND_REDESIGN.md 的指示执行前端视觉改造：

1. `CLAUDE.md` — 了解项目技术栈、端口、代码规范
2. `docs/UI_DESIGN.md` — 了解现有 UI 设计规范
3. `FRONTEND_REDESIGN.md` — 本次改造的完整规格（新增文件，在项目根目录）

**执行前请确认**：
- 前端服务运行在 :6010，可以通过浏览器预览
- 改造过程中保持后端 :6011 正常运行以便真实数据预览
- 每完成一个 Step 做一次 git commit

**从 Step 1 开始执行。**
