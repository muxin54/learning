"""
第11课 演示 —— Header 请求头 与 Cookie
"""
from fastapi import FastAPI, Header, Cookie, Response

app = FastAPI(title="第11课 - Header 与 Cookie")


# ============================================================
# 一、Header —— 读取请求头
# ============================================================
# Header() 从请求头里取数据
# HTTP 头原本是 kebab-case（如 user-agent），Python 变量不能用中划线
# FastAPI 会自动转换：User-Agent → user_agent

@app.get("/whoami")
async def whoami(
    user_agent: str = Header(),           # 浏览器标识（自动从 User-Agent 取）
    accept_language: str = Header(default="zh-CN"),  # 有默认值 → 可选
):
    """看看谁在访问我"""
    return {
        "browser": user_agent,
        "language": accept_language,
    }


# ============================================================
# 二、自定义响应头
# ============================================================
# Response 对象可以让你在返回数据的同时，加响应头

@app.get("/custom-header")
async def custom_header(response: Response):
    """返回时在响应头里加点自定义信息"""
    response.headers["X-App-Name"] = "名片管理系统"
    response.headers["X-Response-Time"] = "42ms"
    return {"message": "响应头已设置，打开浏览器开发者工具 → Network 查看"}


# ============================================================
# 三、Cookie —— 读取
# ============================================================
# Cookie() 用法和 Header() 几乎一样

@app.get("/read-cookie")
async def read_cookie(
    session_id: str = Cookie(default=""),       # 从 Cookie 里取 session_id
    last_visit: str = Cookie(default="从未"),    # 从 Cookie 里取 last_visit
):
    """读取浏览器发来的 Cookie"""
    return {
        "session_id": session_id if session_id else "未设置",
        "last_visit": last_visit,
    }


# ============================================================
# 四、Cookie —— 写入
# ============================================================
# 用 Response.set_cookie() 往浏览器里种 Cookie

@app.get("/set-cookie")
async def set_cookie(response: Response):
    """往浏览器里种几个 Cookie"""
    response.set_cookie(
        key="session_id",
        value="abc123",
        max_age=3600,        # 有效期，秒（3600 = 1小时）
        httponly=True,       # 前端 JS 无法读取，防 XSS 攻击
    )
    response.set_cookie(
        key="last_visit",
        value="2026-06-29",
        max_age=86400,       # 一天
    )
    return {"message": "Cookie 已种下！去 /read-cookie 看看"}


# ============================================================
# 五、综合示例 —— 真实场景：访问计数
# ============================================================
@app.get("/visit-counter")
async def visit_counter(
    response: Response,
    visit_count: str = Cookie(default="0"),  # 读 Cookie
):
    """每次访问计数 +1，存进 Cookie"""
    count = int(visit_count) + 1
    response.set_cookie(
        key="visit_count",
        value=str(count),
        max_age=3600,
    )
    return {
        "message": f"你今天访问了 {count} 次",
        "visit_count": count,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
