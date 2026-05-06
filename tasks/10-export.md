# 10 Word/Markdown导出

## 目标

导出原始转写记录和会议纪要。

## 格式

V1支持：

- Markdown
- Word docx

## 导出内容

### 原始转写

- 会议基础信息
- 参会人
- 时间戳
- 说话人
- 分段文本

### 会议纪要

- 标题
- 摘要
- 会议内容
- 行动项
- 风险点
- 下一步计划

## API

- `POST /api/meetings/{meeting_id}/export-transcript`
- `POST /api/summaries/{summary_id}/export`
- `GET /api/export-records/{export_id}/download`

## 验收

可下载docx文件，内容清晰可读。
