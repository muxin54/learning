"""
auth.py —— JWT 令牌工具
负责：生成令牌（登录用）、验证令牌（后续请求用）
"""
from datetime import datetime, timedelta,timezone
from jose import JWTError, jwt
from app.config import settings

# ============================================
# 配置（真实项目放环境变量，这里先写死）
# ============================================
SECRET_KEY = settings.secret_key  # 签名密钥，绝对不能泄露
ALGORITHM = settings.algorithm          # 签名算法
EXPIRE_MINUTES = settings.expire_minutes           # 令牌有效期（分钟）


def create_token(data: dict) -> str:
    """
    生成 JWT 令牌
    参数：data = {"sub": 用户ID}
    返回：一串加密字符串（令牌）

    比喻：银行柜台给你打印的排号纸条
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=EXPIRE_MINUTES)
    to_encode["exp"] = expire  # exp = 过期时间，到期自动失效
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict | None:
    """
    验证并解析令牌
    成功 → 返回令牌里的数据 {"sub": 用户ID}
    失败 → 返回 None

    比喻：柜员检查你的排号纸条是不是真的、有没有过号
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None  # 令牌无效（伪造的 / 过期了）
