"""
第9课 演示文件 —— response_model 的作用
运行：python demo_response_model.py
然后浏览器打开 http://127.0.0.1:8000/docs 对比三个接口
"""
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="response_model 演示")


# 模拟数据库中的用户数据（有密码等敏感字段）
class UserInDB:
    """假设这是数据库查出来的用户对象"""
    def __init__(self):
        self.id = 1
        self.username = "zhangsan"
        self.password = "abc123"          # ← 密码！绝对不能返回给前端！
        self.phone = "13800138000"
        self.is_admin = True              # ← 内部权限标记，也不该暴露
        self.internal_note = "VIP客户"    # ← 内部备注


# --------- 定义一个"对外安全"的响应模型 ---------
class UserPublic(BaseModel):
    """给前端看的用户信息 —— 只包含能公开的字段"""
    id: int
    username: str
    phone: str


# ================================================================
# 接口1：❌ 不用 response_model —— 全部字段暴露
# ================================================================
@app.get("/user/unsafe")
def get_user_unsafe():
    """危险写法：直接把数据库对象摊开返回"""
    user = UserInDB()
    return user.__dict__  # 返回所有属性，包括 password！
    # 前端会看到：{"id":1, "username":"zhangsan", "password":"abc123", ...}


# ================================================================
# 接口2：✅ 用 response_model —— 自动过滤
# ================================================================
@app.get("/user/safe", response_model=UserPublic)
def get_user_safe():
    """安全写法：用 response_model 过滤，只返回 UserPublic 里定义的字段"""
    user = UserInDB()
    return user.__dict__
    # FastAPI 会自动只返回 id、username、phone，password 等自动丢弃！
    # 前端只会看到：{"id":1, "username":"zhangsan", "phone":"13800138000"}


# ================================================================
# 接口3：同样用 response_model，但返回的是 Pydantic 模型对象
# ================================================================
@app.get("/user/safe2", response_model=UserPublic)
def get_user_safe2():
    """即使返回的对象字段比模型多，也会被自动裁剪"""
    user = UserInDB()
    return user  # FastAPI 会从 user 中提取 UserPublic 需要的字段


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
