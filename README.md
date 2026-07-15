# 名片管理系统 — FastAPI 后端 API

一个基于 FastAPI 的后端 API 项目，支持名片管理、待办事项、博客文章和用户认证。适合作为学习 FastAPI 的完整范例。

## 技术栈

| 分类 | 技术 |
|------|------|
| **框架** | FastAPI (Python 3.11) |
| **数据库** | PostgreSQL + SQLAlchemy（异步 asyncpg） |
| **认证** | JWT（python-jose + bcrypt 密码加密） |
| **部署** | Docker + docker-compose |
| **测试** | pytest + TestClient |
| **配置** | pydantic-settings + .env 环境变量 |

## 功能模块

| 模块 | 功能 |
|------|------|
| 📇 名片管理 | CRUD + 模糊搜索 + 分页 + 文件上传（头像） |
| ✅ 待办事项 | CRUD + 完成状态过滤 + 分页（公开看/增删改需登录） |
| 📝 博客系统 | 文章发布/修改/删除 + 评论功能（只能改自己的） |
| 👤 用户认证 | 注册 + 登录 + JWT 令牌 + 权限保护（401/403） |

## API 文档

启动后访问 Swagger 文档：

```
http://127.0.0.1:8001/docs
```

## 项目结构

```
fastapi-learning/
├── app/
│   ├── main.py              ← 应用入口（lifespan、中间件、异常处理）
│   ├── config.py            ← 配置管理（pydantic-settings）
│   ├── database.py          ← PostgreSQL 异步连接
│   ├── models.py            ← ORM 模型（Card/User/Todo/Post/Comment）
│   ├── schemas.py           ← Pydantic 请求/响应模型
│   ├── auth.py              ← JWT 创建与验证
│   ├── dependencies.py      ← 分页依赖（Depends 复用）
│   ├── logging_config.py    ← 日志配置（控制台 + 文件双写）
│   ├── routers/
│   │   ├── cards.py         ← 名片 CRUD + 文件上传 + Cookie
│   │   ├── users.py         ← 注册/登录/JWT 鉴权
│   │   ├── todo.py          ← 待办 CRUD（部分接口需登录）
│   │   └── posts.py         ← 博客文章 + 评论
│   └── test_todo.py         ← pytest 测试用例
├── demo_*.py                ← 各课演示文件（11 个）
├── Dockerfile               ← Docker 镜像菜谱
├── docker-compose.yml       ← 一键启动 API + PostgreSQL
├── requirements.txt         ← 依赖清单
└── .env.example             ← 环境变量示例（实际 .env 不提交）
```

## 快速启动

### 1. 克隆项目

```bash
git clone https://github.com/muxin54/learning.git
cd learning
```

### 2. 创建虚拟环境并安装依赖

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 3. 创建 .env 文件

复制 `.env.example` 为 `.env`，根据你的环境修改数据库连接等信息。

### 4. 启动 PostgreSQL

确保 PostgreSQL 在运行（端口 5433），数据库名为 `fastapi_learning`。

或者在项目根目录用 Docker Compose 一键启动（API + 数据库）：

```bash
docker compose up -d
```

### 5. 启动应用

```bash
# 本地开发
uvicorn app.main:app --reload --port 8001

# 生产环境
uvicorn app.main:app --workers 4 --port 8001
```

### 6. 访问

打开 `http://127.0.0.1:8001/docs` 查看 API 文档。

## 运行测试

```bash
python -m pytest app/test_todo.py -v
```

## 常用命令速查

| 操作 | 命令 |
|------|------|
| 启动服务 | `uvicorn app.main:app --reload --port 8001` |
| 启动数据库 | `sc.exe start PostgreSQL` |
| Docker 构建 | `docker build -t card-api .` |
| Docker 运行 | `docker run -d --name card-api -p 8000:8000 --env-file .env card-api` |
| 运行测试 | `python -m pytest app/test_todo.py -v` |

## 核心知识点

本项目覆盖了 FastAPI 学习路线的全部 28 课内容：

- ✅ 路径参数、查询参数、请求体（Pydantic）
- ✅ response_model 响应过滤
- ✅ Form 表单 + 文件上传（UploadFile）
- ✅ Header、Cookie 读写
- ✅ 错误处理（HTTPException + 全局异常兜底）
- ✅ Field 校验 + 嵌套模型
- ✅ PostgreSQL + SQLAlchemy 异步 ORM
- ✅ APIRouter 多文件项目组织
- ✅ Depends 依赖注入深入（依赖链、类依赖、工厂模式）
- ✅ 中间件（请求计时 + 日志记录）
- ✅ CORS 跨域配置
- ✅ pydantic-settings + .env 配置管理
- ✅ JWT 认证（OAuth2PasswordBearer + 权限保护）
- ✅ pytest 测试（TestClient + 鉴权测试）
- ✅ Swagger 文档美化（summary/description/tags）
- ✅ 健康检查 + 日志落盘
- ✅ Docker 容器化部署

## License

MIT

