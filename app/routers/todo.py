from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Todo
from app.schemas import TodoCreate, TodoOut, TodoUpdate

router = APIRouter(prefix="/todos", tags=["待办事项"])


# ============================================
# GET —— 列表（可选 done 过滤）
# ============================================
@router.get("/", response_model=list[TodoOut])
async def get_all(
    done: bool = None,                        # None=全部  True=已完成  False=未完成
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Todo).order_by(Todo.id.desc())
    if done is not None:
        stmt = stmt.where(Todo.done == done)
    result = await session.execute(stmt)
    return result.scalars().all()


# ============================================
# GET —— 查单个
# ============================================
@router.get("/{todo_id}", response_model=TodoOut)
async def get_one(todo_id: int, session: AsyncSession = Depends(get_session)):
    todo = await session.get(Todo, todo_id)        # ← 这里用的是 todo_id，不是 todo.id
    if not todo:
        raise HTTPException(status_code=404, detail="待办找不到")
    return todo


# ============================================
# POST —— 新增
# ============================================
@router.post("/", status_code=201, response_model=TodoOut)
async def add_one(data: TodoCreate, session: AsyncSession = Depends(get_session)):
    todo = Todo(**data.model_dump())               # 把 Pydantic 数据塞进 ORM 对象
    session.add(todo)                               # 加入会话
    await session.commit()                          # 提交到数据库
    await session.refresh(todo)                     # 刷新（拿到数据库生成 id、created_at）
    return todo                                     # response_model 自动过滤


# ============================================
# PUT —— 修改（部分更新）
# ============================================
@router.put("/{todo_id}", response_model=TodoOut)
async def update_one(
    todo_id: int,
    data: TodoUpdate,
    session: AsyncSession = Depends(get_session),
):
    # ① 查
    todo = await session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="待办找不到")

    # ② 只更新前端传了的字段
    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return todo                                 # 啥都没传就原样返回

    for key, value in update_data.items():
        setattr(todo, key, value)                  # 动态赋值：todo.title = "新标题"

    # ③ 提交
    await session.commit()
    await session.refresh(todo)
    return todo


# ============================================
# DELETE —— 删除
# ============================================
@router.delete("/{todo_id}")
async def delete_one(todo_id: int, session: AsyncSession = Depends(get_session)):
    todo = await session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="待办找不到")

    await session.delete(todo)                      # 标记删除
    await session.commit()                          # 提交到数据库
    return {"message": f"待办 {todo_id} ({todo.title}) 已删除"}
