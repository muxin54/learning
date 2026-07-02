"""
第二章第1课：PostgreSQL + FastAPI 联动
把"个人名片"改成 PostgreSQL 数据库存储
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import databases

# ============================================
# 1. 数据库连接配置
# ============================================

# asyncpg 是 Python 里连 PostgreSQL 最快的异步驱动
# 格式：postgresql://用户名:密码@地址:端口/数据库名
DATABASE_URL = "postgresql://postgres@localhost:5433/fastapi_learning"
#                         ↑ 用户名    ↑ 地址:端口  ↑ 数据库名（已建好）

database = databases.Database(DATABASE_URL)
# ↑ database 就是你和数据库之间的"电话线"，之后所有查询都用它

# ============================================
# 2. FastAPI 应用
# ============================================

app = FastAPI(title="名片管理（PostgreSQL 版）", version="3.0.0")


# ============================================
# 3. 建表 SQL
# ============================================

# 和 MySQL 的 CREATE TABLE 几乎一模一样
CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS cards (
    id      SERIAL PRIMARY KEY,         -- SERIAL = 自动递增整数（MySQL 的 AUTO_INCREMENT）
    name    VARCHAR(50) NOT NULL,       -- 姓名，最长50字符，不能为空
    title   VARCHAR(100) DEFAULT '',    -- 职位，默认空
    phone   VARCHAR(20) DEFAULT '',     -- 手机号，默认空
    email   VARCHAR(100) DEFAULT '',    -- 邮箱，默认空
    company VARCHAR(100) DEFAULT ''     -- 公司，默认空
);
"""


# 启动时：连接数据库 + 建表，关闭时：断开连接
@app.on_event("startup")
async def startup():
    await database.connect()            # 先连上数据库
    await database.execute(CREATE_TABLE_SQL)  # 再检查/建表
    print("PostgreSQL 已连接，表 cards 已就绪")


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("PostgreSQL 已断开")


# ============================================
# 4. Pydantic 请求体模型（和以前一模一样）
# ============================================

class CardCreate(BaseModel):
    """新增名片"""
    name: str
    title: str = ""
    phone: str = ""
    email: str = ""
    company: str = ""


class CardUpdate(BaseModel):
    """修改名片（全部选填 = 改什么传什么）"""
    name: str | None = None
    title: str | None = None
    phone: str | None = None
    email: str | None = None
    company: str | None = None


# ============================================
# 5. CRUD 接口
# ============================================

# ---- GET：列表（搜索 + 分页）----

@app.get("/cards")
async def list_cards(keyword: str = "", page: int = 1, page_size: int = 10):
    """
    名片列表，支持搜索姓名和分页
    /cards                          → 全部
    /cards?keyword=张                → 搜姓名带"张"的
    /cards?page=2&page_size=5       → 分页
    """
    if keyword:
        # ILIKE：PG 的大小写不敏感 LIKE（MySQL 的 LIKE 默认不敏感，PG 要加 I）
        # %keyword%：前后加 % 表示"包含"，和 MySQL 的 LIKE '%keyword%' 一样
        count_query = "SELECT COUNT(*) FROM cards WHERE name ILIKE :kw"
        data_query = """
            SELECT * FROM cards
            WHERE name ILIKE :kw
            ORDER BY id DESC
            LIMIT :limit OFFSET :offset
        """
        values = {"kw": f"%{keyword}%"}
    else:
        count_query = "SELECT COUNT(*) FROM cards"
        data_query = """
            SELECT * FROM cards
            ORDER BY id DESC
            LIMIT :limit OFFSET :offset
        """
        values = {}

    total = await database.fetch_val(count_query, values=values)
    values.update({"limit": page_size, "offset": (page - 1) * page_size})
    rows = await database.fetch_all(data_query, values=values)

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size if total else 0,
        "data": [dict(row) for row in rows],
    }


# ---- GET：查单个 ----

@app.get("/cards/{card_id}")
async def get_one(card_id: int):
    """查单张名片"""
    row = await database.fetch_one(
        "SELECT * FROM cards WHERE id = :id",
        values={"id": card_id}
    )
    if not row:
        raise HTTPException(status_code=404, detail="名片不存在")
    return dict(row)


# ---- POST：新增 ----

@app.post("/cards", status_code=201)
async def create_card(card: CardCreate):
    """新增名片"""
    # INSERT ... RETURNING id：插入后直接拿到自动生成的 id
    # MySQL 用 LAST_INSERT_ID()，PG 用 RETURNING id，更直接
    insert_query = """
        INSERT INTO cards(name, title, phone, email, company)
        VALUES (:name, :title, :phone, :email, :company)
        RETURNING id
    """
    new_id = await database.fetch_val(insert_query, values=card.model_dump())

    # 查回来返回（为了一致性，包含所有字段）
    card_data = await database.fetch_one(
        "SELECT * FROM cards WHERE id = :id",
        values={"id": new_id}
    )
    return dict(card_data)


# ---- PUT：修改 ----

@app.put("/cards/{card_id}")
async def update_card(card_id: int, card: CardUpdate):
    """修改名片（只改传了的字段）"""
    # 只取前端实际传了的字段（exclude_unset=True 的作用和以前一样）
    update_data = card.model_dump(exclude_unset=True)
    if not update_data:
        # 啥也没传，直接返回原数据
        row = await database.fetch_one(
            "SELECT * FROM cards WHERE id = :id",
            values={"id": card_id}
        )
        if not row:
            raise HTTPException(status_code=404, detail="名片不存在")
        return {"message": "没有需要更新的字段", "card": dict(row)}

    # 动态拼 SET 子句：SET name=:name, title=:title ...
    # 这和 MySQL 的 UPDATE 语法完全一样
    set_parts = [f"{key} = :{key}" for key in update_data]
    query = f"UPDATE cards SET {', '.join(set_parts)} WHERE id = :id"
    update_data["id"] = card_id

    await database.execute(query, values=update_data)

    # 返回更新后的数据
    card_data = await database.fetch_one(
        "SELECT * FROM cards WHERE id = :id",
        values={"id": card_id}
    )
    if not card_data:
        raise HTTPException(status_code=404, detail="名片不存在")
    return {"message": "修改成功", "card": dict(card_data)}


# ---- DELETE：删除 ----

@app.delete("/cards/{card_id}")
async def delete_card(card_id: int):
    """删除名片"""
    # 先查在不在
    row = await database.fetch_one(
        "SELECT * FROM cards WHERE id = :id",
        values={"id": card_id}
    )
    if not row:
        raise HTTPException(status_code=404, detail="名片不存在")

    await database.execute("DELETE FROM cards WHERE id = :id", values={"id": card_id})
    return {"message": f"名片 {card_id} 已删除"}

