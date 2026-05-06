# 06 转写编辑

## 目标

用户可以查看、编辑、保存转写结果。

## 功能

- 按时间顺序展示片段
- 显示开始/结束时间
- 支持修改文本
- 支持修改说话人标签
- 支持合并生成完整文本

## API

- `GET /api/meetings/{meeting_id}/transcript-segments`
- `PUT /api/transcript-segments/{segment_id}`
- `PUT /api/meetings/{meeting_id}/corrected-text`

## 验收

用户编辑片段后，刷新页面仍能保留修改。
