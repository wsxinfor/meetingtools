# 数据结构 + API 设计

## 1. 核心实体关系

```text
Customer 1 ── N Project 1 ── N Meeting
Meeting 1 ── N AudioFile
Meeting 1 ── N TranscriptSegment
Meeting 1 ── N MeetingSummary
MeetingTemplate 1 ── N MeetingSummary
LlmConfig N ── N MeetingSummary（通过 llm_config_id 关联）
TermDictionary 用于纠错
AsrTask / LlmTask 用于异步任务追踪
ExportRecord 用于导出文件追踪
```

## 2. 数据表设计

### 2.1 customers 客户表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| name | varchar | 客户名称 |
| industry | varchar | 行业 |
| contact_info | jsonb | 联系人信息 |
| notes | text | 备注 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 2.2 projects 项目表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| customer_id | uuid | 客户ID |
| name | varchar | 项目名称 |
| stage | varchar | 项目阶段 |
| budget | varchar | 预算描述 |
| notes | text | 备注 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 2.3 meetings 会议表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| customer_id | uuid | 客户ID，可空 |
| project_id | uuid | 项目ID，可空 |
| title | varchar | 会议标题 |
| meeting_type | varchar | 会议类型 |
| meeting_time | timestamp | 会议时间 |
| participants | jsonb | 参会人 |
| status | varchar | 状态：draft/uploaded/processing/done/failed |
| raw_text | text | 完整原始识别文本 |
| corrected_text | text | 纠错后文本 |
| summary_text | text | 默认纪要文本 |
| error_message | text | 错误信息 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 2.4 audio_files 音频文件表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| meeting_id | uuid | 会议ID |
| original_filename | varchar | 原始文件名 |
| file_path | varchar | 原始音频路径 |
| normalized_path | varchar | 预处理后wav路径 |
| duration_seconds | numeric | 时长 |
| sample_rate | integer | 采样率 |
| channels | integer | 声道数 |
| status | varchar | uploaded/preprocessed/failed |
| created_at | timestamp | 创建时间 |

### 2.5 transcript_segments 转写片段表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| meeting_id | uuid | 会议ID |
| audio_file_id | uuid | 音频ID |
| segment_index | integer | 片段序号 |
| start_ms | integer | 开始毫秒 |
| end_ms | integer | 结束毫秒 |
| speaker_label | varchar | 说话人标签，如 speaker_1 |
| raw_text | text | 原始识别文本 |
| corrected_text | text | 修改/纠错后文本 |
| confidence | numeric | 置信度，可空 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 2.6 meeting_templates 会议模板表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| name | varchar | 模板名称 |
| type | varchar | 模板类型 |
| description | text | 描述 |
| prompt_text | text | Prompt内容 |
| output_schema | jsonb | 输出结构预留 |
| enabled | boolean | 是否启用 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 2.7 meeting_summaries 纪要表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| meeting_id | uuid | 会议ID |
| template_id | uuid | 模板ID |
| title | varchar | 纪要标题 |
| content_md | text | Markdown纪要 |
| content_json | jsonb | 结构化纪要 |
| version | integer | 版本 |
| is_final | boolean | 是否最终版 |
| llm_config_id | uuid | 生成时使用的 LLM 配置 ID，可空 |
| llm_model | varchar | 实际使用的模型名，冗余存储便于追溯 |
| created_at | timestamp | 创建时间 |

### 2.8 term_dictionary 术语库表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| category | varchar | 分类：brand/product/customer/common |
| wrong_text | varchar | 常见错误 |
| correct_text | varchar | 正确词 |
| aliases | jsonb | 别名 |
| enabled | boolean | 是否启用 |
| created_at | timestamp | 创建时间 |

### 2.9 llm_configs LLM配置表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| name | varchar | 配置名称，如"本地Ollama"、"GPT-4o" |
| provider | varchar | ollama / openai_compatible |
| base_url | varchar | API endpoint，如 http://localhost:11434/v1 |
| api_key | varchar | API Key（外部服务需要，本地可为空，加密存储） |
| model_name | varchar | 模型名称，如 qwen2.5:7b、gpt-4o |
| is_default | boolean | 是否为默认配置 |
| is_enabled | boolean | 是否启用 |
| created_at | timestamp | 创建时间 |
| updated_at | timestamp | 更新时间 |

### 2.10 asr_tasks ASR任务表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| meeting_id | uuid | 会议ID |
| audio_file_id | uuid | 音频ID |
| engine | varchar | funasr/sensevoice/whisper |
| status | varchar | pending/running/done/failed |
| progress | integer | 进度0-100 |
| error_message | text | 错误信息 |
| started_at | timestamp | 开始时间 |
| finished_at | timestamp | 完成时间 |
| created_at | timestamp | 创建时间 |

### 2.11 export_records 导出记录表

| 字段 | 类型 | 说明 |
|---|---|---|
| id | uuid | 主键 |
| meeting_id | uuid | 会议ID |
| summary_id | uuid | 纪要ID，可空 |
| export_type | varchar | transcript/summary |
| file_format | varchar | docx/md/pdf/json |
| file_path | varchar | 文件路径 |
| created_at | timestamp | 创建时间 |

## 3. API设计

### 3.1 会议管理

#### 创建会议

`POST /api/meetings`

请求：

```json
{
  "title": "客户超融合方案交流",
  "meeting_type": "presales",
  "customer_id": "可空",
  "project_id": "可空",
  "meeting_time": "2026-04-28T10:00:00",
  "participants": ["张三", "李四"]
}
```

#### 获取会议列表

`GET /api/meetings?keyword=&customer_id=&project_id=&status=&page=1&page_size=20`

#### 获取会议详情

`GET /api/meetings/{meeting_id}`

#### 更新会议

`PUT /api/meetings/{meeting_id}`

#### 删除会议

`DELETE /api/meetings/{meeting_id}`

### 3.2 音频上传与录音

#### 上传音频

`POST /api/meetings/{meeting_id}/audio`

multipart/form-data：

- file: 音频文件

返回：

```json
{
  "audio_file_id": "uuid",
  "status": "uploaded"
}
```

#### 获取音频信息

`GET /api/audio-files/{audio_file_id}`

### 3.3 ASR识别

#### 启动识别任务

`POST /api/meetings/{meeting_id}/asr-tasks`

请求：

```json
{
  "audio_file_id": "uuid",
  "engine": "funasr",
  "enable_vad": true,
  "enable_punctuation": true
}
```

返回：

```json
{
  "task_id": "uuid",
  "status": "pending"
}
```

#### 查询任务状态

`GET /api/asr-tasks/{task_id}`

#### 重新识别片段

`POST /api/transcript-segments/{segment_id}/rerun-asr`

### 3.4 转写文本

#### 获取片段列表

`GET /api/meetings/{meeting_id}/transcript-segments`

#### 更新单个片段文本

`PUT /api/transcript-segments/{segment_id}`

请求：

```json
{
  "corrected_text": "修改后的文本",
  "speaker_label": "客户张总"
}
```

#### 保存完整纠错文本

`PUT /api/meetings/{meeting_id}/corrected-text`

### 3.5 术语库

`GET /api/terms`

`POST /api/terms`

`PUT /api/terms/{term_id}`

`DELETE /api/terms/{term_id}`

#### 对会议执行术语纠错

`POST /api/meetings/{meeting_id}/apply-terms`

### 3.6 模板管理

`GET /api/templates`

`POST /api/templates`

`PUT /api/templates/{template_id}`

`DELETE /api/templates/{template_id}`

### 3.7 纪要生成

#### 生成纪要

`POST /api/meetings/{meeting_id}/summaries`

请求：

```json
{
  "template_id": "uuid",
  "source": "corrected_text",
  "llm_config_id": "uuid（可空，为空时使用默认配置）"
}
```

#### 获取纪要列表

`GET /api/meetings/{meeting_id}/summaries`

#### 更新纪要

`PUT /api/summaries/{summary_id}`

### 3.8 LLM 配置管理

#### 获取配置列表

`GET /api/llm-configs`

#### 创建配置

`POST /api/llm-configs`

请求：

```json
{
  "name": "本地 Ollama",
  "provider": "ollama",
  "base_url": "http://localhost:11434/v1",
  "api_key": "",
  "model_name": "qwen2.5:7b",
  "is_default": true
}
```

#### 更新配置

`PUT /api/llm-configs/{config_id}`

#### 删除配置

`DELETE /api/llm-configs/{config_id}`

#### 设为默认

`PUT /api/llm-configs/{config_id}/set-default`

#### 测试连接

`POST /api/llm-configs/{config_id}/test`

返回：

```json
{
  "code": 0,
  "data": {
    "success": true,
    "latency_ms": 320,
    "sample_output": "你好，我是..."
  },
  "msg": "ok"
}
```

### 3.9 导出

#### 导出转写记录

`POST /api/meetings/{meeting_id}/export-transcript`

请求：

```json
{
  "format": "docx"
}
```

#### 导出会议纪要

`POST /api/summaries/{summary_id}/export`

请求：

```json
{
  "format": "docx"
}
```

#### 下载导出文件

`GET /api/export-records/{export_id}/download`

## 4. ASR部署设计

### 4.1 开发阶段

允许开发机安装 FunASR，用于：

- 验证识别效果
- 调试 ffmpeg/VAD/ASR流程
- 本地跑通接口

### 4.2 生产阶段

正式使用时，ASR 应部署在服务器上：

```text
前端浏览器 → FastAPI → ASR服务/FunASR → 返回文本
```

### 4.3 建议抽象接口

后端不要把业务代码写死到 FunASR，应抽象为：

```python
class AsrProvider:
    def transcribe(self, audio_path: str) -> list[TranscriptSegment]:
        pass
```

具体实现：

- LocalFunAsrProvider
- HttpAsrProvider
- WhisperProvider

这样后续可以从开发机本地调用平滑切换到服务器ASR服务。

