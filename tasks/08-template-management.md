# 08 模板管理

## 目标

实现会议纪要Prompt模板的增删改查。

## 默认模板

- 通用会议纪要
- 售前客户交流
- 项目推进会议
- 技术方案讨论
- 招投标沟通

## API

- `GET /api/templates`
- `POST /api/templates`
- `PUT /api/templates/{template_id}`
- `DELETE /api/templates/{template_id}`

## 验收

用户可在页面编辑模板Prompt，并保存到数据库。
