"""
第二章第2课：SQLAlchemy ORM 操作 PostgreSQL
用 Python 类操作数据库，告别手写 SQL
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, select, func, or_, delete as sa_delete, update as sa_update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# ============================================
# 1. 数据库连接配置
# ============================================

# asyncpg 驱动 + PostgreSQL
DATABASE_URL = "postgresql+asyncpg://postgres@localhost:5433/fastapi_learning"
#             ↑ 注意多了一个 +asyncpg，SQLAlchemy 需要知道用什么驱动

# 创建异步引擎 —— 和昨天 databases 的作用一样，但更底层
engine = create_async_engine(DATABASE_URL, echo=False)
# echo=True 会打印所有 SQL 语句（调试时开），echo=False 关了

# 创建会话工厂 —— 每次请求从这儿拿一个 session
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# 基类
Base = declarative_base()

# ============================================
# 2. 定义 ORM 模型（一张表 = 一个类）
# ============================================

class Card(Base):
    """
    数据库 cards 表的 Python 映射
    对比昨天的 CREATE TABLE：
      id      SERIAL PRIMARY KEY  →  Integer, primary_key=True
      name    VARCHAR(50) NOT NULL →  String(50), nullable=False
      title   VARCHAR(100) DEFAULT '' → String(100), default=''
    """
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    title = Column(String(100), default="")
    phone = Column(String(20), default="")
    email = Column(String(100), default="")
    company = Column(String(100), default="")

    def __repr__(self):
        """打印对象时友好显示（调试用）"""
        return f"<Card(id={self.id}, name='{self.name}', title='{self.title}')>"


# ============================================
# 3. Pydantic 请求体模型（和昨天一模一样）
# ============================================

class CardCreate(BaseModel):
    name: str
    title: str = ""
    phone: str = ""
    email: str = ""
    company: str = ""


class CardUpdate(BaseModel):
    name: str | None = None
    title: str | None = None
    phone: str | None = None
    email: str | None = None
    company: str | None = None


# ============================================
# 4. FastAPI 应用
# ============================================

app = FastAPI(title="名片管理（ORM 版）", version="4.0.0")


# 启动时建表 + 关闭时断连
@app.on_event("startup")
async def startup():
    # create_all：扫描所有继承 Base 的模型，自动建表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()


# ============================================
# 5. 依赖注入：每次请求自动获取/释放 session
# ============================================

async def get_session():
    """
    这个函数就是"管家"：
    每次请求来了 → 创建一个新 session → 用完自动关闭
    类比：每次去游泳，管理员给你一把储物柜钥匙，游完了还回去
    """
    async with AsyncSessionLocal() as session:
        yield session  # yield：把 session 交给接口函数，函数跑完了回到这里关闭


# ============================================
# 6. CRUD 接口（用 ORM 写法）
# ============================================

from fastapi import Depends

# ---- GET：列表 ----

@app.get("/cards")
async def list_cards(
    keyword: str = "",
    company: str = "",      # ← 新增：按公司搜索
    page: int = 1,
    page_size: int = 10,
    session: AsyncSession = Depends(get_session)
):
    """
    名片列表，支持按姓名搜索 + 按公司搜索 + 分页
    keyword: 模糊匹配 name 字段
    company: 模糊匹配 company 字段（两个条件可以同时用）
    """
    # ---- 第1步：拼总数查询 ----
    stmt = select(func.count()).select_from(Card)
    if keyword:
        stmt = stmt.where(or_(
            Card.name.ilike(f"%{keyword}%"),
            Card.company.ilike(f"%{keyword}%")
        ))
    if company:
        stmt = stmt.where(Card.company.ilike(f"%{company}%"))
    total = (await session.execute(stmt)).scalar()

    # ---- 第2步：拼数据查询 ----
    stmt = select(Card).order_by(Card.id.desc())
    if keyword:
        stmt = stmt.where(or_(
            Card.name.ilike(f"%{keyword}%"),
            Card.company.ilike(f"%{keyword}%")
        ))
    if company:              # ← 新增
        stmt = stmt.where(Card.company.ilike(f"%{company}%"))
    stmt = stmt.limit(page_size).offset((page - 1) * page_size)

    result = await session.execute(stmt)
    cards = result.scalars().all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total else 0,
        "data": [
            {"id": c.id, "name": c.name, "title": c.title,
             "phone": c.phone, "email": c.email, "company": c.company}
            for c in cards
        ],
    }


# ---- GET：查单个 ----

@app.get("/cards/{card_id}")
async def get_one(card_id: int, session: AsyncSession = Depends(get_session)):
    """查单张名片"""
    card = await session.get(Card, card_id)  # 按主键查，一行搞定！
    if not card:
        raise HTTPException(status_code=404, detail="名片不存在")

    return {
        "id": card.id, "name": card.name, "title": card.title,
        "phone": card.phone, "email": card.email, "company": card.company,
    }


# ---- POST：新增 ----

@app.post("/cards", status_code=201)
async def create_card(card_in: CardCreate, session: AsyncSession = Depends(get_session)):
    """新增名片"""
    # 直接 new 一个 Python 对象
    card = Card(**card_in.model_dump())
    #       ↑ ** 是解包：Card(name="张三", title="文职", ...)

    session.add(card)       # 加入会话（= 标记为"待插入"）
    await session.commit()  # 提交事务（= 真正写入数据库）
    await session.refresh(card)  # 刷新 = 拿到数据库自动生成的 id

    return {
        "id": card.id, "name": card.name, "title": card.title,
        "phone": card.phone, "email": card.email, "company": card.company,
    }


# ---- PUT：修改 ----

@app.put("/cards/{card_id}")
async def update_card(
    card_id: int,
    card_in: CardUpdate,
    session: AsyncSession = Depends(get_session)
):
    """修改名片（部分更新）"""
    card = await session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="名片不存在")

    update_data = card_in.model_dump(exclude_unset=True)
    if not update_data:
        return {"message": "没有需要更新的字段"}

    # 直接改对象属性
    for key, value in update_data.items():
        setattr(card, key, value)  # 等价于 card.name = "新名字"

    await session.commit()   # 提交 → SQLAlchemy 自动生成 UPDATE SQL
    await session.refresh(card)

    return {"message": "修改成功", "card": {
        "id": card.id, "name": card.name, "title": card.title,
        "phone": card.phone, "email": card.email, "company": card.company,
    }}


# ---- DELETE：删除 ----

@app.delete("/cards/{card_id}")
async def delete_card(card_id: int, session: AsyncSession = Depends(get_session)):
    """删除名片 —— 先查再删，用 RETURNING 思路"""
    card = await session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="名片不存在")

    await session.delete(card)   # 标记删除
    await session.commit()       # 真正删除

    return {"message": f"名片 {card_id} ({card.name}) 已删除"}
