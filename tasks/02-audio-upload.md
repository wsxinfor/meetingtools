# 02 音频上传与文件管理

## 目标

支持给会议上传音频文件，并保存文件元数据。

## 要求

- 支持 mp3、wav、m4a、aac
- 限制文件大小配置化
- 文件按 meeting_id 分目录保存
- 写入 audio_files 表

## API

- `POST /api/meetings/{meeting_id}/audio`
- `GET /api/audio-files/{audio_file_id}`

## 验收

上传音频后，会议详情页能看到文件名、大小、状态。
