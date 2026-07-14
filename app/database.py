"""
database.py —— 数据库连接配置
原来在 main_orm.py 最上面那一坨，现在独立成一个文件
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings

# PostgreSQL 连接地址（和之前一模一样）
DATABASE_URL =settings.database_url

# 创建异步引擎 —— 这是和数据库通信的"底层通道"
engine = create_async_engine(DATABASE_URL, echo=False)
# echo=True → 会打印每条 SQL，调试时有用，正式跑关了就行

# 创建会话工厂 —— 每次请求来就从这里拿一个新的 session
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# 基类 —— 所有 ORM 模型都要继承它
Base = declarative_base()


async def get_session():
    """
    获取数据库会话的依赖函数
    每次请求自动创建 session → 用完自动关闭
    类比：游泳馆管理员，你来给你钥匙，你走收回钥匙
    """
    async with AsyncSessionLocal() as session:
        yield session
