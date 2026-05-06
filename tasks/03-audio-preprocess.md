# 03 音频预处理

## 目标

使用 ffmpeg 将原始音频转换为 ASR 标准输入。

## 标准格式

- wav
- 16kHz
- 单声道
- 音量归一化

## 后端服务

创建：

```text
services/audio/preprocess.py
```

核心函数：

```python
def normalize_audio(input_path: str, output_path: str) -> AudioMeta:
    pass
```

## 示例命令

```bash
ffmpeg -y -i input.mp3 -ac 1 -ar 16000 -af "loudnorm" output.wav
```

## API

可以由 ASR 任务自动触发，也可以提供内部接口。

## 验收

上传任意支持格式音频后，可生成标准wav文件，并记录路径。
