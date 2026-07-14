"""
第22课 演示 —— 公开接口 vs 受保护接口
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

app = FastAPI(title="第22课 - 接口权限保护")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# 模拟用户数据
fake_users = {
    1: {"id": 1, "username": "zhangsan", "role": "admin"},
    2: {"id": 2, "username": "lisi", "role": "user"},
}
fake_tokens = {
    "token-1": 1,   # token-1 → zhang san
    "token-2": 2,   # token-2 → lisi
}


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """模拟鉴权：从请求头取 token → 找用户"""
    user_id = fake_tokens.get(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="未登录或 token 无效")
    return fake_users[user_id]


# ============================================================
# 公开接口 — 不需要登录
# ============================================================
@app.get("/public/hello")
async def public_hello():
    """任何人都能访问"""
    return {"message": "你好，游客！这里是公开信息"}


@app.get("/public/list")
async def public_list():
    """不登录也能看"""
    return ["item1", "item2", "item3"]


# ============================================================
# 受保护接口 — 需要登录
# ============================================================
@app.get("/private/profile")
async def private_profile(user: dict = Depends(get_current_user)):
    """必须登录才能看 —— 加一行 Depends(get_current_user) 就够了"""
    return {
        "message": f"欢迎回来，{user['username']}！",
        "user_id": user["id"],
        "role": user["role"],
    }


# ============================================================
# 权限分级 —— 只允许 admin
# ============================================================
async def require_admin(user: dict = Depends(get_current_user)):
    """在 get_current_user 基础上再加一层检查"""
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")
    return user


@app.get("/admin/users")
async def admin_list_users(admin: dict = Depends(require_admin)):
    """仅管理员能访问 —— 依赖链：require_admin → get_current_user → token"""
    return {
        "message": "管理员面板",
        "all_users": list(fake_users.values()),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
