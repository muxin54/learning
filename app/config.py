"""
config.py —— 集中管理所有配置（读取 .env 文件）
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """项目所有配置的集中管理"""

    # ---- 数据库 ----
    database_url: str = "postgresql+asyncpg://postgres@localhost:5433/fastapi_learning"

    # ---- JWT ----
    secret_key: str = "dev-secret"
    algorithm: str = "HS256"
    expire_minutes: int = 60

    # ---- 应用 ----
    app_name: str = "我的API"
    debug: bool = True

    model_config = {"env_file": ".env"}


# 全局唯一配置对象 —— 其他模块直接导入这个
settings = Settings()
