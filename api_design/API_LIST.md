# API清单速览

## 客户 / 项目

- `GET /api/customers`
- `POST /api/customers`
- `PUT /api/customers/{id}`
- `DELETE /api/customers/{id}`
- `GET /api/projects`
- `POST /api/projects`
- `PUT /api/projects/{id}`
- `DELETE /api/projects/{id}`

## 会议

- `POST /api/meetings`
- `GET /api/meetings`
- `GET /api/meetings/{id}`
- `PUT /api/meetings/{id}`
- `DELETE /api/meetings/{id}`

## 音频

- `POST /api/meetings/{meeting_id}/audio`
- `GET /api/audio-files/{audio_file_id}`

## ASR

- `POST /api/meetings/{meeting_id}/asr-tasks`
- `GET /api/asr-tasks/{task_id}`
- `POST /api/transcript-segments/{segment_id}/rerun-asr`

## 转写

- `GET /api/meetings/{meeting_id}/transcript-segments`
- `PUT /api/transcript-segments/{segment_id}`
- `PUT /api/meetings/{meeting_id}/corrected-text`

## 术语

- `GET /api/terms`
- `POST /api/terms`
- `PUT /api/terms/{term_id}`
- `DELETE /api/terms/{term_id}`
- `POST /api/meetings/{meeting_id}/apply-terms`

## 模板

- `GET /api/templates`
- `POST /api/templates`
- `PUT /api/templates/{template_id}`
- `DELETE /api/templates/{template_id}`

## LLM 配置

- `GET /api/llm-configs`
- `POST /api/llm-configs`
- `PUT /api/llm-configs/{config_id}`
- `DELETE /api/llm-configs/{config_id}`
- `PUT /api/llm-configs/{config_id}/set-default`
- `POST /api/llm-configs/{config_id}/test`

## 纪要

- `POST /api/meetings/{meeting_id}/summaries`
- `GET /api/meetings/{meeting_id}/summaries`
- `PUT /api/summaries/{summary_id}`

## 导出

- `POST /api/meetings/{meeting_id}/export-transcript`
- `POST /api/summaries/{summary_id}/export`
- `GET /api/export-records/{export_id}/download`
