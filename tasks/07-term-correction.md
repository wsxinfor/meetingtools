# 07 术语库与自动纠错

## 目标

实现术语库维护和自动替换纠错。

## 功能

- 新增术语
- 编辑术语
- 禁用术语
- 对会议文本执行纠错

## 纠错策略

第一版先做规则替换：

```text
wrong_text → correct_text
```

第二版再接入本地LLM做上下文纠错。

## API

- `GET /api/terms`
- `POST /api/terms`
- `PUT /api/terms/{term_id}`
- `DELETE /api/terms/{term_id}`
- `POST /api/meetings/{meeting_id}/apply-terms`

## 验收

维护术语后，可对会议转写文本批量替换。
