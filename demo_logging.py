"""
第27课 演示 —— 日志、健康检查、性能优化
"""
import logging
import time
from fastapi import FastAPI, Request

app = FastAPI(title="第27课 - 日志与性能")


# ============================================================
# 一、配置日志
# ============================================================
# Python 内置的 logging 模块，比 print() 强一万倍
# print() 只能打屏幕上，logging 可以同时打屏幕 + 写文件 + 发邮件

logging.basicConfig(
    level=logging.INFO,                    # 只记录 INFO 及以上级别
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),           # 输出到控制台
        logging.FileHandler("app.log", encoding="utf-8"),  # 同时写到文件
    ],
)
logger = logging.getLogger("card-api")     # 创建本项目的日志器


# ============================================================
# 二、日志级别 —— 什么时候用哪个
# ============================================================
# DEBUG   → 调试信息，开发时用（变量值、SQL）
# INFO    → 正常流程记录（"用户张三登录成功"）
# WARNING → 不太对劲但还能跑（"密码尝试失败"）
# ERROR   → 出错了（"数据库连接失败"）
# CRITICAL → 系统要挂了（"磁盘满了"）

@app.get("/test-log")
async def test_log():
    logger.debug("这是调试信息，默认不输出（级别太低）")
    logger.info("这是一条普通日志")
    logger.warning("这是一条警告")
    logger.error("这是一条错误日志")
    return {"message": "日志已输出到控制台和 app.log 文件"}


# ============================================================
# 三、健康检查（你已经有了，这里是扩展版）
# ============================================================
# 简单的：return "ok"   —— 你已经写了
# 完善的：检查数据库、Redis 等依赖是否正常

@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查 —— 负载均衡器/监控系统定期来测"""
    # 真实项目会在这检查：
    #   - 数据库能连吗？
    #   - Redis 能连吗？
    #   - 磁盘够用吗？
    return {
        "status": "healthy",
        "version": "6.0.0",
    }


# ============================================================
# 四、性能优化技巧
# ============================================================

# ① 限制分页大小 —— 防刷
MAX_PAGE_SIZE = 100   # 单次最多返回 100 条

# ② 真正耗时的 I/O 操作才用 async（数据库查询、网络请求）
#    纯 CPU 计算（循环、数学运算）不要用 async，反而更慢

# ③ 生产环境不再用 --reload
#    --reload 每次请求都检查文件变化，消耗 CPU
#    生产环境：uvicorn app.main:app --workers 4
#    workers = CPU 核心数，没有 --reload


@app.get("/slow-demo")
async def slow_demo():
    """故意慢的接口 —— 演示长耗时问题的排查"""
    time.sleep(2)
    return {"message": "这个接口卡了2秒，日志里能看到"}


# ============================================================
# 五、中间件记录所有请求（升级版）
# ============================================================
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """每个请求自动记日志"""
    logger.info(f"→ {request.method} {request.url.path} 来自 {request.client.host}")
    start = time.time()
    response = await call_next(request)
    elapsed = time.time() - start
    logger.info(f"← {request.method} {request.url.path} {response.status_code} {elapsed:.3f}s")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
