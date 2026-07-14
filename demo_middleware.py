"""
第19课 演示 —— 中间件与 CORS
"""
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="第19课 - 中间件与CORS")


# ============================================================
# 一、自定义中间件 —— 请求计时
# ============================================================
@app.middleware("http")                          # ← 标记为 HTTP 中间件
async def add_process_time(request: Request, call_next):
    """
    每个请求进来时：
      ① 记一下开始时间
      ② call_next(request) 让请求继续走（进入你的接口函数）
      ③ 拿到响应后，记结束时间
      ④ 在响应头里加上 X-Process-Time
    """
    start = time.time()                         # ① 开始计时
    response = await call_next(request)         # ② 放行 → 接口函数执行
    process_time = time.time() - start          # ③ 计算耗时
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"  # ④ 写入响应头
    return response


# ============================================================
# 二、测试接口
# ============================================================
@app.get("/fast")
async def fast():
    return {"msg": "这个接口很快"}

@app.get("/slow")
async def slow():
    time.sleep(0.5)   # 模拟慢操作
    return {"msg": "这个接口故意慢了 0.5 秒"}


# ============================================================
# 三、CORS 跨域 —— 为什么需要它
# ============================================================
# 浏览器安全策略：禁止一个域名（http://localhost:3000 前端）调用另一个域名（http://localhost:8001 后端）
# CORS 就是告诉浏览器："允许这些域名来访问我"

# ⚠️ 不加 CORS 的话：
#    前端页面如果用 fetch("http://localhost:8001/cards") → 浏览器直接拦截，请求根本发不出去

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:5500"],  # 允许哪些前端域名
    allow_credentials=True,                              # 允许携带 Cookie
    allow_methods=["GET", "POST", "PUT", "DELETE"],     # 允许哪些 HTTP 方法
    allow_headers=["*"],                                 # 允许哪些请求头（* = 全部）
)

# 开发阶段简单粗暴的写法（只限本地开发！）：
# allow_origins=["*"]   ← 允许所有域名，不安全但省事


# ============================================================
# 四、中间件 vs 依赖注入 —— 怎么选
# ============================================================
# | 需求 | 用什么 |
# |------|--------|
# | 所有请求都要干的活 | 中间件 |
# | 特定接口才需要的 | 依赖注入 Depends |
# | 举例：计时、打日志 | 中间件 |
# | 举例：鉴权、拿当前用户 | 依赖注入 |


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
