"""
routers/users.py —— 用户认证接口（注册 + 登录 + 个人信息）
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt

from app.database import get_session
from app.models import User
from app.schemas import UserRegister, UserLogin
from app.auth import create_token, decode_token

router = APIRouter(prefix="/users", tags=["用户认证"])

# ============================================
# 密码加密工具（直接用 bcrypt，不依赖 passlib）
# ============================================
# bcrypt 是一种加密算法：
#   明文 "123456" → 加密后 → "$2b$12$k8H...一堆看不懂的字符"
#   永远存加密后的，即使数据库泄露，黑客也不知道用户密码是啥


def hash_password(password: str) -> str:
    """把明文密码加密成哈希值"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """验证密码是否正确"""
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


# ============================================
# JWT 验证依赖（告诉 FastAPI"谁在访问"）
# ============================================
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")
# ↑ tokenUrl 就是你的登录接口地址
#   FastAPI 用它做两件事：
#     1. /docs 右上角的 🔓 锁图标 → 点开就是登录弹窗 → 自动调这个接口拿 token
#     2. 解析请求头：取出 "Authorization: Bearer xxx" 里的 token 字符串


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    这个函数是"门禁系统"：
    从请求头取出 token → 解码 → 查到用户 → 返回用户对象

    用法：让接口依赖这个函数，就能拿到"当前登录的用户"
    """
    # 第1步：验证令牌
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="令牌无效或已过期，请重新登录")

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="令牌内容不完整")

    # 第2步：查用户还在不在（可能被删了）
    user = await session.get(User, int(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")

    return user


# ============================================
# POST —— 注册
# ============================================
@router.post(
    "/register",
    status_code=201,
    summary="用户注册",
    description="注册新账号，用户名不可重复，密码使用 bcrypt 加密存储。",
    response_description="注册成功的用户信息（不含密码）",
)
async def register(req: UserRegister, session: AsyncSession = Depends(get_session)):
    """
    注册接口
    前端传：{"username": "张三", "password": "123456"}
    我们做：
      1. 检查用户名有没有被占
      2. 密码加密
      3. 写入数据库
    """
    # 第1步：检查是否已被注册
    stmt = select(User).where(User.username == req.username)
    existing = (await session.execute(stmt)).scalar()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已被注册")

    # 第2步：加密密码
    hashed_pw = hash_password(req.password)
    # "123456" → "$2b$12$..." （黑客看不到原始密码）

    # 第3步：写入数据库
    user = User(username=req.username, password=hashed_pw)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {
        "message": "注册成功",
        "user": {"id": user.id, "username": user.username}
    }


# ============================================
# POST —— 登录
# ============================================
@router.post(
    "/login",
    summary="用户登录",
    description="验证用户名和密码，返回 JWT 令牌用于后续受保护的接口。",
    response_description="JWT 令牌（access_token）",
)
async def login(req: UserLogin, session: AsyncSession = Depends(get_session)):
    """
    登录接口
    前端传：{"username": "张三", "password": "123456"}
    我们做：
      1. 查用户
      2. 核对密码
      3. 返回 JWT 令牌
    """
    # 第1步：查用户
    stmt = select(User).where(User.username == req.username)
    user = (await session.execute(stmt)).scalar()
    if not user:
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    # 第2步：核对密码
    if not verify_password(req.password, user.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")

    # 第3步：发令牌
    token = create_token({"sub": str(user.id)})
    # sub 是 JWT 标准字段，放"当前是谁"的标识

    return {
        "message": "登录成功",
        "access_token": token,
        "token_type": "bearer"
    }


# ============================================
# GET —— 查看个人信息（需要登录才能访问）
# ============================================
@router.get(
    "/me",
    summary="查看个人信息（需登录）",
    description="根据请求头携带的 JWT 令牌返回当前登录用户的信息。",
    response_description="当前用户信息",
)
async def get_me(
    user: User = Depends(get_current_user)  # ← 依赖注入：自动验证身份
):
    """
    查看我自己的信息
    客户端请求头必须带：Authorization: Bearer <令牌>
    """
    return {"id": user.id, "username": user.username}
