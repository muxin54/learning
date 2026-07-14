"""
第20课 演示 —— 配置管理与环境变量
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# ============================================================
# 第1步：加载 .env 文件
# ============================================================
# load_dotenv() 会读取项目根目录的 .env 文件，把里面的 KEY=VALUE
# 加载到系统环境变量中，然后通过 os.getenv() 获取
load_dotenv()


# ============================================================
# 第2步：定义 Settings 类（把所有配置集中在一起）
# ============================================================
class Settings(BaseSettings):
    """项目所有配置的集中管理"""
    # 数据库
    database_url: str = "sqlite:///./test.db"  # 默认值（如果 .env 没配就用这个）

    # JWT
    secret_key: str = "dev-secret"              # .env 有 SECRET_KEY 就自动覆盖
    algorithm: str = "HS256"
    expire_minutes: int = 60

    # 应用
    app_name: str = "我的API"
    debug: bool = True

    model_config = {"env_file": ".env"}         # Pydantic v2 的配置方式


settings = Settings()

# ============================================================
# 使用示例
# ============================================================
print("=" * 50)
print("当前配置：")
print(f"  数据库URL: {settings.database_url}")
print(f"  密钥:      {settings.secret_key[:8]}...（已隐藏）")
print(f"  应用名:    {settings.app_name}")
print(f"  Debug:     {settings.debug}")
print("=" * 50)
print()
print("工作原理：")
print("  ① Settings 类定义字段和默认值")
print("  ② 启动时自动读取 .env 文件")
print("  ③ .env 里的值覆盖默认值")
print("  ④ 代码里 settings.字段名 直接取值")

if __name__ == "__main__":
    print()
    print("运行 FastAPI:")
    print("  from app.config import settings")
    print("  DATABASE_URL = settings.database_url  # 不用写死！")
