# 05 ASR识别模块（FunASR）

## 目标

封装本地ASR识别能力，识别音频片段并生成转写文本。

## 架构要求

必须抽象 AsrProvider：

```python
class AsrProvider:
    def transcribe_file(self, audio_path: str):
        pass
```

实现：

- LocalFunAsrProvider：开发机或服务器本地调用
- HttpAsrProvider：调用独立ASR服务
- MockAsrProvider：测试用

## 部署说明

开发阶段：

- FunASR可以安装在开发机器上调试

生产阶段：

- FunASR应部署在服务器或独立容器
- FastAPI通过AsrProvider调用

## API

- `POST /api/meetings/{meeting_id}/asr-tasks`
- `GET /api/asr-tasks/{task_id}`

## 验收

上传音频后，启动ASR任务，可以生成每个片段的 raw_text。
