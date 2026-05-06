# 04 VAD切分与片段管理

## 目标

检测有效人声片段，生成时间戳切片。

## 推荐方案

优先使用 FunASR VAD 或 Silero VAD。

## 输出

写入 transcript_segments 初始记录：

- segment_index
- start_ms
- end_ms
- speaker_label 可空
- raw_text 为空

## 要求

- 过滤长静音
- 片段不宜过短或过长
- 保留原始时间戳

## 验收

一段长音频可切出多个有效语音片段。
