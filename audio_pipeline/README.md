# 音频处理链路设计

## 1. 链路

```text
原始音频
↓
ffmpeg预处理
↓
VAD切分
↓
ASR识别
↓
片段文本拼接
↓
术语纠错/LLM纠错
↓
模板提取
```

## 2. ffmpeg预处理

目标：统一格式，降低ASR输入复杂度。

标准输出：

- wav
- 16kHz
- 单声道
- 音量归一化

命令：

```bash
ffmpeg -y -i input.mp3 -ac 1 -ar 16000 -af "loudnorm" output.wav
```

## 3. VAD切分

目标：找出有效人声片段。

作用：

- 去掉静音
- 长音频切短
- 提升识别稳定性
- 支持并行识别

## 4. ASR识别

推荐：

- FunASR / SenseVoiceSmall 为主
- Whisper为备用

## 5. 片段结构

```json
{
  "start_ms": 1200,
  "end_ms": 8500,
  "speaker_label": "speaker_1",
  "raw_text": "识别文本",
  "corrected_text": "纠错文本"
}
```
