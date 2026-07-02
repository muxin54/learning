"""
第12课 演示 —— 错误处理与异常
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="第12课 - 错误处理")


# ============================================================
# 一、HTTPException —— 各种状态码
# ============================================================
# 你已经很熟了，复习几种常用状态码：

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    """演示不同的错误情况"""
    if item_id <= 0:
        raise HTTPException(status_code=400, detail="ID 必须大于 0")
        # 400 = 客户端参数有误

    if item_id == 42:
        raise HTTPException(status_code=401, detail="你没有权限查看此项目")
        # 401 = 未认证

    if item_id == 99:
        raise HTTPException(status_code=403, detail="你身份没问题，但没有权限操作")
        # 403 = 已认证但无权限（401 vs 403 的区别）

    if item_id == 404:
        raise HTTPException(status_code=404, detail="项目不存在")
        # 404 = 资源找不到

    return {"item_id": item_id, "name": f"项目{item_id}"}


# ============================================================
# 二、自定义异常处理器 —— 拦截特定异常
# ============================================================
# 场景：项目里某个地方没查到数据，我们想统一返回格式

# ① 定义自己的异常类（继承 Python 标准 Exception）
class ItemNotFoundError(Exception):
    """自定义异常：物品不存在"""
    def __init__(self, item_id: int):
        self.item_id = item_id
        self.message = f"物品 {item_id} 没有找到"


# ② 注册异常处理器 —— 告诉 FastAPI "如果出现这个异常，按这个格式返回"
@app.exception_handler(ItemNotFoundError)
async def item_not_found_handler(request: Request, exc: ItemNotFoundError):
    """捕获 ItemNotFoundError，返回统一的 JSON"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "NOT_FOUND",
            "message": exc.message,
            "item_id": exc.item_id,
        }
    )


# ③ 使用自定义异常
@app.get("/products/{product_id}")
async def get_product(product_id: int):
    """如果产品不存在，抛自定义异常，格式由处理器统一控制"""
    if product_id > 100:
        raise ItemNotFoundError(item_id=product_id)
    return {"product_id": product_id, "name": f"产品{product_id}"}


# ============================================================
# 三、全局异常兜底 —— 兜住所有"没想到的错误"
# ============================================================
# 生产环境必须加这个，否则报错信息会泄露代码细节

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """兜底：任何没被特定处理器捕获的异常，统一返回 500"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_ERROR",
            "message": "服务器内部错误",
            # ⚠️ 生产环境不要返回 exc 的详细信息，会泄露代码！
        }
    )


@app.get("/crash")
async def crash():
    """故意崩溃，测试全局兜底"""
    x = 1 / 0  # ZeroDivisionError → 会被全局处理器捕获
    return {"result": x}


# ============================================================
# 四、校验错误也统一（422 → 友好中文）
# ============================================================
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    """把 FastAPI 默认的英文校验错误改成中文格式"""
    errors = exc.errors()
    # 提取第一条错误，翻译成中文
    detail = errors[0] if errors else {}
    msg = f"参数校验失败：{detail.get('msg', '未知错误')}"
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": msg,
            "fields": [e.get("loc", []) for e in errors],
        }
    )


@app.get("/validate")
async def validate(q: int):
    """测试校验：传非数字会触发 422"""
    return {"q": q}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
