# meeting-ai × local-asr-service 集成说明

## 配置

在 meeting-ai 服务的环境变量中添加：

```env
ASR_SERVICE_BASE_URL=http://192.168.10.71:18080/api
ASR_SERVICE_API_KEY=<your-api-key>
```

API Key 由 local-asr-service 管理员在 Web 管理端创建：**Web 管理端 → API客户端 → 新建客户端**，创建后复制 key 提供给对接方。

---

## 完整调用流程

```
meeting-ai                          local-asr-service
    |                                      |
    |── POST /v1/transcriptions ──────────>|  上传音频，返回 task_id
    |<── { task_id, status:"queued" } ─────|
    |                                      |
    |── GET  /v1/transcriptions/{id} ─────>|  轮询（每 5s）
    |<── { status, progress } ─────────────|
    |      ... 重复直到 status == "done"    |
    |                                      |
    |── GET  /v1/transcriptions/{id}/result>|  获取结构化结果
    |<── { full_text, segments[] } ─────────|
    |                                      |
    |  写入 transcript_segments             |
    |  继续: 纠错 / 纪要 / 导出             |
```

---

## API 说明

### 上传音频

```http
POST /api/v1/transcriptions
Authorization: Bearer <API_KEY>
Content-Type: multipart/form-data
```

| 字段 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `file` | File | 必填 | 音频文件（mp3/m4a/wav/flac 等） |
| `language` | string | `zh` | 识别语言：`zh` / `en` / `auto` |
| `enable_vad` | bool | `true` | 启用 VAD 分段 |
| `enable_punctuation` | bool | `true` | 启用标点恢复 |
| `enable_diarization` | bool | `false` | 启用说话人分离（cam++，CPU 较慢） |
| `enable_filler_removal` | bool | `false` | 去除口语填充词（嗯、啊、那个…） |
| `enable_llm_correction` | bool | `false` | 启用 LLM 二次校正（需服务端配置 LLM，可选） |
| `hotword_set_id` | UUID | null | 热词集 ID，提升专有名词识别率 |

**响应** `202 Accepted`：

```json
{
  "success": true,
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "queued"
  }
}
```

---

### 查询任务状态

```http
GET /api/v1/transcriptions/{task_id}
Authorization: Bearer <API_KEY>
```

**响应**：

```json
{
  "success": true,
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "recognizing",
    "progress": 55,
    "engine": "funasr",
    "language": "zh",
    "duration_seconds": 312.4,
    "enable_diarization": false,
    "created_at": "2025-05-15T10:00:00Z",
    "started_at": "2025-05-15T10:00:03Z",
    "finished_at": null,
    "error_message": null
  }
}
```

**`status` 取值**：

| 值 | 含义 |
|---|---|
| `queued` | 已入队，等待 worker 处理 |
| `preprocessing` | ffmpeg 归一化音频 |
| `segmenting` | VAD 分段 |
| `recognizing` | FunASR 推理中 |
| `postprocessing` | 热词纠错 + 生成导出文件 |
| `done` | 完成，可获取结果 |
| `failed` | 失败，见 `error_message` |
| `cancelled` | 已取消 |

---

### 获取识别结果

```http
GET /api/v1/transcriptions/{task_id}/result
Authorization: Bearer <API_KEY>
```

仅 `status == "done"` 时可调用，否则返回 `409`。

**响应**：

```json
{
  "success": true,
  "data": {
    "task_id": "550e8400-e29b-41d4-a716-446655440000",
    "engine": "funasr",
    "duration_seconds": 312.4,
    "full_text": "各位好，今天我们来讨论一下今年的技术规划……",
    "segments": [
      {
        "index": 0,
        "start_ms": 0,
        "end_ms": 4200,
        "speaker_id": null,
        "text": "各位好，今天我们来讨论一下今年的技术规划。",
        "confidence": null
      },
      {
        "index": 1,
        "start_ms": 4800,
        "end_ms": 9100,
        "speaker_id": "SPEAKER_00",
        "text": "首先我来介绍一下超融合架构的现状。",
        "confidence": null
      }
    ]
  }
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|---|---|---|
| `task_id` | UUID | 任务 ID |
| `engine` | string | 识别引擎（固定 `funasr`） |
| `duration_seconds` | float\|null | 音频时长（秒） |
| `full_text` | string | 全文拼接（所有分段 `text` 顺序拼接） |
| `segments[].index` | int | 分段序号（从 0 开始） |
| `segments[].start_ms` | int | 分段开始时间（毫秒） |
| `segments[].end_ms` | int | 分段结束时间（毫秒） |
| `segments[].speaker_id` | string\|null | 说话人标签（`SPEAKER_00` 等，仅开启 diarization 时有值） |
| `segments[].text` | string | 分段识别文本（已做热词纠错和口语词去除） |
| `segments[].confidence` | float\|null | 置信度（当前版本为 null） |

---

### 下载导出文件

```http
GET /api/v1/transcriptions/{task_id}/download?format=srt
Authorization: Bearer <API_KEY>
```

`format` 取值：`json` / `txt` / `srt` / `vtt`

直接返回文件内容（`Content-Type: text/plain` 或 `application/json`）。

---

## Python 示例

见 [`meeting_ai_client.py`](meeting_ai_client.py)。

```python
from meeting_ai_client import transcribe

# 上传、等待完成、返回 transcript_segments
segments = transcribe(
    "meeting.mp3",
    enable_diarization=True,
    enable_filler_removal=True,
    hotword_set_id="your-hotword-set-uuid",
)

# 写入 meeting-ai 数据库
for seg in segments:
    db.transcript_segments.insert(
        meeting_id=meeting_id,
        sequence=seg["sequence"],
        start_ms=seg["start_ms"],
        end_ms=seg["end_ms"],
        speaker=seg["speaker"],
        text=seg["text"],
    )
```

## curl 示例

见 [`meeting_ai_curl.sh`](meeting_ai_curl.sh)。

```bash
ASR_BASE_URL=http://your-server:18080/api \
ASR_API_KEY=asr_xxxx \
bash meeting_ai_curl.sh meeting.mp3
```

---

## 错误处理建议

| 错误码 | HTTP | 含义 | 处理方式 |
|---|---|---|---|
| `UNAUTHORIZED` | 401 | API Key 无效或未提供 | 检查 `Authorization` header |
| `UNSUPPORTED_FORMAT` | 400 | 文件格式不支持 | 转换为 mp3/wav |
| `FILE_TOO_LARGE` | 413 | 超过 `MAX_UPLOAD_SIZE_MB` | 分段上传或调整配置 |
| `TASK_NOT_FOUND` | 404 | task_id 不存在 | 检查 task_id |
| `TASK_NOT_DONE` | 409 | 任务未完成时请求 result | 等待 `status == done` |

网络超时或 5xx 错误时，可对上传和轮询分别做指数退避重试。
