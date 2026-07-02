"""
routers/cards.py —— 名片 CRUD 接口
原来的增删改查逻辑原封不动搬过来，只是换了 import 的来源
"""
import os

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile,Header,Cookie,Response
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from app.database import get_session
from app.models import Card
from app.schemas import CardCreate, CardUpdate,CardOut,CardListResponse

# 创建路由器 —— 把所有 /cards 相关的接口都挂在它下面
router = APIRouter(prefix="/cards", tags=["名片管理"])


# ============================================
# GET —— 列表（搜索 + 分页）
# ============================================
@router.get("/",response_model=CardListResponse)
async def list_cards(
    keyword: str = "",
    company: str = "",
    page: int = 1,
    page_size: int = 10,
    session: AsyncSession = Depends(get_session),
    
):
    """名片列表：支持按姓名/公司搜索 + 分页"""
    # 查总数
    stmt = select(func.count()).select_from(Card)
    if keyword:
        stmt = stmt.where(or_(
            Card.name.ilike(f"%{keyword}%"),
            Card.company.ilike(f"%{keyword}%")
        ))
    if company:
        stmt = stmt.where(Card.company.ilike(f"%{company}%"))
    total = (await session.execute(stmt)).scalar()

    # 查数据
    stmt = select(Card).order_by(Card.id.desc())
    if keyword:
        stmt = stmt.where(or_(
            Card.name.ilike(f"%{keyword}%"),
            Card.company.ilike(f"%{keyword}%")
        ))
    if company:
        stmt = stmt.where(Card.company.ilike(f"%{company}%"))
    stmt = stmt.limit(page_size).offset((page - 1) * page_size)

    result = await session.execute(stmt)
    cards = result.scalars().all()
    
    return {
    "total": total,
    "page": page,
    "page_size": page_size,
    "total_pages": (total + page_size - 1) // page_size if total else 0,
    "data": cards,
}

@router.get("/stats/access")
async def cookie_count(response:Response,first_visit:str=Cookie(default="")):
    if not first_visit:
        now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        response.set_cookie(key="first_visit",value=now)
        return {"message": "第一次来，欢迎！", "first_visit": now}
    else:
        return {"message": "欢迎回来", "first_visit": first_visit}
        


# ============================================
# GET —— 查单个
# ============================================
@router.get("/{card_id}",response_model=CardOut)
async def get_one(card_id: int, session: AsyncSession = Depends(get_session)):
    """根据 ID 查一张名片"""
    card = await session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="名片不存在")
    
    return card


# ============================================
# POST —— 新增
# ============================================
@router.post("/", status_code=201)
async def create_card(card_in: CardCreate, session: AsyncSession = Depends(get_session)):
    """新增一张名片"""
    card = Card(**card_in.model_dump())
    session.add(card)
    await session.commit()
    await session.refresh(card)
    return {
        "id": card.id, "name": card.name, "title": card.title,
        "phone": card.phone, "email": card.email, "company": card.company,
    }


# ============================================
# PUT —— 修改
# ============================================
@router.put("/{card_id}")
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

    for key, value in update_data.items():
        setattr(card, key, value)

    await session.commit()
    await session.refresh(card)
    return {"message": "修改成功", "card": {
        "id": card.id, "name": card.name, "title": card.title,
        "phone": card.phone, "email": card.email, "company": card.company,
    }}


# ============================================
# DELETE —— 删除
# ============================================
@router.delete("/{card_id}")
async def delete_card(card_id: int, session: AsyncSession = Depends(get_session)):
    """删除一张名片"""
    card = await session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="名片不存在")

    await session.delete(card)
    await session.commit()
    return {"message": f"名片 {card_id} ({card.name}) 已删除"}

# ============================================
# POST —— 上传名片头像
# ============================================
@router.post("/{card_id}/avatar")
async def upload_avatar(
    card_id: int,                                     # 路径参数：名片ID
    file: UploadFile = File(),                       # 文件字段：上传的图片
    session: AsyncSession = Depends(get_session),    # 数据库会话
):
    """为指定名片上传头像图片"""
    # ① 先查名片在不在 —— 和 get_one 一样的套路
    card = await session.get(Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="名片不存在")

    # ② 确保 uploads 目录存在（exist_ok=True 表示目录已存在也不报错）
    os.makedirs("uploads", exist_ok=True)

    # ③ 拼接文件名：名片ID_原始文件名，避免同文件名被覆盖
    filename = f"{card_id}_{file.filename}"
    save_path = os.path.join("uploads", filename)

    # ④ 读取文件内容并写入磁盘
    content = await file.read()           # await：异步读取，不阻塞服务器
    with open(save_path, "wb") as f:      # wb = 二进制写入模式
        f.write(content)                  # 把字节写入文件

    return {
        "message": "头像上传成功",
        "path": save_path,
        "filename": file.filename,
    }



