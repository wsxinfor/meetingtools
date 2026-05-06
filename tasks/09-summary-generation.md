# 09 会议纪要生成

## 目标

调用 LLM，根据模板生成会议纪要。支持本地 Ollama 和外部 OpenAI 兼容服务，可在前端配置和测试 LLM 连接。

## LLM 要求

- 通过统一 `LlmProvider` 调用，底层统一使用 OpenAI SDK（`openai` Python 包）
- 本地 Ollama：`base_url=http://localhost:6014/v1`，`api_key="ollama"`
- 外部 OpenAI 兼容：任意 `base_url` + `api_key`，如 OpenAI、DeepSeek、硅基流动等
- 多个配置可共存，指定其中一个为默认

## 输入

- `corrected_text`（纠错后全文）
- `template.prompt_text`（模板 Prompt）
- 会议基础信息（标题、时间、参会人）
- `llm_config_id`（可空，空则取默认配置）

## 输出

- Markdown 格式纪要
- 结构化 JSON 预留（V2）

## 数据表

依赖 `llm_configs` 表（见 DATA_API_DESIGN 2.9 节）。

`meeting_summaries` 表新增字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| llm_config_id | uuid | 生成时使用的 LLM 配置，可空 |
| llm_model | varchar | 实际使用的模型名，冗余存储 |

## API

- `GET /api/llm-configs` — 获取配置列表
- `POST /api/llm-configs` — 创建配置
- `PUT /api/llm-configs/{config_id}` — 更新配置
- `DELETE /api/llm-configs/{config_id}` — 删除配置
- `PUT /api/llm-configs/{config_id}/set-default` — 设为默认
- `POST /api/llm-configs/{config_id}/test` — 测试连接（返回延迟和样本输出）
- `POST /api/meetings/{meeting_id}/summaries` — 生成纪要（携带可选 `llm_config_id`）
- `GET /api/meetings/{meeting_id}/summaries` — 获取纪要列表
- `PUT /api/summaries/{summary_id}` — 更新纪要

## 前端页面

**LLM 配置页**（系统设置中）：

- 配置列表，显示名称、类型（本地/外部）、模型、是否默认
- 新增/编辑表单：名称、provider 类型、base_url、api_key（密码框）、model_name
- 每条配置有"测试连接"按钮，显示成功/失败及延迟
- 设为默认按钮

## 验收

1. 可创建本地 Ollama 配置并测试连通
2. 可创建外部 OpenAI 兼容配置并测试连通
3. 选择模板后，可生成一版会议纪要
4. 纪要记录中可查看使用的模型名称
5. 生成的纪要允许人工修改
