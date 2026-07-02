"""
main.py —— FastAPI 应用入口（公司大门）
负责：启动 app、注册路由器、启动/关闭时维护数据库
"""
from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.routers import cards, users,todo
from fastapi.exceptions import RequestValidationError

app = FastAPI(title="名片管理系统", version="5.0.0")


# ---- 启动时自动建表 ----
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ---- 关闭时断开数据库 ----
@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


# ---- 注册路由器 ----
app.include_router(cards.router)   # 名片管理
app.include_router(users.router)   # 用户认证（注册/登录）
app.include_router(todo.router)


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