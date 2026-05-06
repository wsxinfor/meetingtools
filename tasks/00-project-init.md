# 00 项目初始化

## 目标

建立可运行的前后端基础项目和Docker开发环境。

## 后端任务

- 创建 FastAPI 项目结构
- 配置 SQLAlchemy async
- 配置 PostgreSQL
- 配置 Alembic
- 创建统一配置模块 settings
- 创建健康检查接口 `/api/health`

## 前端任务

- 创建 Vue 3 + TypeScript 项目
- 引入 Element Plus
- 配置路由
- 配置 API 客户端
- 创建基础布局

## Docker任务

- 编写 docker-compose.yml
- 服务包括：backend、frontend、postgres
- 预留 funasr、ollama、minio 服务配置

端口映射（严格按此配置，不得修改）：

```yaml
frontend:  "6010:5173"   # Vite dev server
backend:   "6011:8000"   # uvicorn
postgres:  "6012:5432"
funasr:    "6013:10095"  # 预留，暂不启动
ollama:    "6014:11434"  # 预留，暂不启动
minio:     "6015:9000"   # 预留，暂不启动
```

## 验收

- `docker compose up -d` 可启动
- `/api/health` 返回正常
- 前端首页可访问
