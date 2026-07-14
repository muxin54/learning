from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.routers.users import get_current_user

from app.database import get_session
from app.models import Todo,User
from app.schemas import TodoCreate, TodoOut, TodoUpdate
from app.dependencies import pagination

router = APIRouter(prefix="/todos", tags=["待办事项"])


# ============================================
# GET —— 列表（可选 done 过滤 + 分页）
# ============================================
@router.get(
    "/",
    response_model=list[TodoOut],
    summary="待办列表",
    description="支持 done 过滤（true=已完成 / false=未完成），支持分页。无需登录。",
    response_description="符合条件的待办列表",
)
async def get_all(
    session: AsyncSession = Depends(get_session),
    done: bool = None,                          # 过滤：None=全部  True=已完成  False=未完成
    p: dict = Depends(pagination),              # 分页：自动拿 page 和 page_size
):
    stmt = select(Todo).order_by(Todo.id.desc())
    if done is not None:
        stmt = stmt.where(Todo.done == done)
    stmt = stmt.limit(p["page_size"]).offset(p["offset"])
    result = await session.execute(stmt)
    return result.scalars().all()


# ============================================
# GET —— 查单个
# ============================================
@router.get("/{todo_id}", response_model=TodoOut)
async def get_one(todo_id: int, session: AsyncSession = Depends(get_session),user:User=Depends(get_current_user)):
    todo = await session.get(Todo, todo_id)        # ← 这里用的是 todo_id，不是 todo.id
    if not todo:
        raise HTTPException(status_code=404, detail="待办找不到")
    return todo


# ============================================
# POST —— 新增
# ============================================
@router.post(
    "/",
    status_code=201,
    response_model=TodoOut,
    summary="新增待办（需登录）",
    description="创建一个新的待办事项，必须携带有效的 JWT 令牌。",
    response_description="新创建的待办信息",
)
async def add_one(data: TodoCreate, session: AsyncSession = Depends(get_session),user: User = Depends(get_current_user)):
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
    user: User = Depends(get_current_user)
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
