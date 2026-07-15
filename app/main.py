"""
main.py —— FastAPI 应用入口（公司大门）
负责：启动 app、注册路由器、启动/关闭时维护数据库
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import time

from app.database import engine, Base
from app.routers import cards, users, todo,posts
from app.logging_config import logger          # ← 用 logger 替代 print

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield  # ← 服务器运行中
    # 关闭时
    await engine.dispose()

# ---- tags 元数据（/docs 分组描述） ----
tags_metadata = [
    {"name": "名片管理", "description": "名片 CRUD 增删改查，支持搜索、分页、文件上传。"},
    {"name": "用户认证", "description": "注册、登录、JWT 令牌管理、个人信息查询。"},
    {"name": "待办事项", "description": "个人待办清单，支持完成状态过滤与分页。需登录才能新增/修改/删除。"},
    {"name": "博客文章", "description": "简易博客系统：发文章、评论。公开阅读，发文章/评论需登录，只能修改自己的内容。"},
]

app = FastAPI(
    title="名片管理系统",
    version="6.0.0",
    lifespan=lifespan,
    description="一个管理个人名片和待办事项的后端 API，支持 JWT 认证。",
    openapi_tags=tags_metadata,
)


# ---- 注册路由器 ----
app.include_router(cards.router)   # 名片管理
app.include_router(users.router)   # 用户认证（注册/登录）
app.include_router(todo.router)
app.include_router(posts.router)


# ---- 校验错误美化：把 422 英文改成中文提示 ----
@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    """把 FastAPI 默认的英文校验错误改成中文格式"""
    errors = exc.errors()
    detail = errors[0] if errors else {}
    msg = f"参数校验失败：{detail.get('msg', '未知错误')}"
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": msg,
            "fields": [e.get("loc", []) for e in errors],
        },
    )


# ---- 全局异常兜底：兜住所有没预料到的错误 ----
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """任何没被特定处理器捕获的异常，统一返回 500"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "服务器内部错误",
        },
    )

# ---- 中间件：请求计时 + 日志记录 ----
@app.middleware("http")
async def compute_time(request: Request, call_next):
    logger.info(f"→ {request.method} {request.url.path} 来自 {request.client.host}")
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    logger.info(f"← {request.method} {request.url.path} {response.status_code} {process_time:.3f}s")
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response


@app.get("/health", tags=["系统"], summary="健康检查")
async def health_check():
    """监控系统定期来敲门，检查服务是否正常运行"""
    logger.debug("健康检查通过")   # DEBUG 级别，默认不显示，不刷屏
    return {"status": "healthy", "version": "6.0.0"}