from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Post, Comment, User
from app.schemas import PostCreate, PostUpdate, PostOut, CommentCreate, CommentOut
from app.dependencies import pagination
from app.routers.users import get_current_user

router = APIRouter(prefix="/posts", tags=["博客文章"])


# ============================================================
# GET —— 文章列表（公开，分页）
# ============================================================
@router.get("/", response_model=list[PostOut], summary="文章列表")
async def list_posts(
    session: AsyncSession = Depends(get_session),
    p: dict = Depends(pagination),          # 分页依赖：自动拿 page/page_size/offset
):
    stmt = select(Post).order_by(Post.id.desc())         # 最新文章排前面
    stmt = stmt.limit(p["page_size"]).offset(p["offset"])  # 分页
    result = await session.execute(stmt)
    return result.scalars().all()


# ============================================================
# GET —— 文章详情（公开）
# ============================================================
@router.get("/{post_id}", response_model=PostOut, summary="文章详情")
async def get_one(
    post_id: int,
    session: AsyncSession = Depends(get_session),
):
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    return post


# ============================================================
# POST —— 发文章（需登录，自动绑定当前用户）
# ============================================================
@router.post("/", status_code=201, response_model=PostOut, summary="发布文章")
async def create_post(
    data: PostCreate,                                    # 前端传 title + content
    user: User = Depends(get_current_user),              # 从 token 拿到谁在发
    session: AsyncSession = Depends(get_session),
):
    # model_dump() 把 Pydantic 模型转成字典，** 拆包传参
    # user_id=user.id 把当前用户绑定上去 —— 文章就知道是谁写的了
    post = Post(**data.model_dump(), user_id=user.id)
    session.add(post)
    await session.commit()
    await session.refresh(post)                          # 刷新取到数据库生成的 id、created_at
    return post


# ============================================================
# PUT —— 改文章（需登录，只能改自己的）
# ============================================================
@router.put("/{post_id}", response_model=PostOut, summary="修改文章")
async def update_post(
    post_id: int,
    data: PostUpdate,                                    # 前端传想改的字段（全部可选）
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    if post.user_id != user.id:                          # ← 不是自己的文章不能改
        raise HTTPException(status_code=403, detail="只能修改自己的文章")

    update_data = data.model_dump(exclude_unset=True)     # 只取前端传了的字段
    if not update_data:
        return post                                       # 啥都没传就原样返回
    for key, value in update_data.items():
        setattr(post, key, value)                         # 动态赋值：post.title = "新标题"

    await session.commit()
    await session.refresh(post)
    return post


# ============================================================
# DELETE —— 删文章（需登录，只能删自己的）
# ============================================================
@router.delete("/{post_id}", summary="删除文章")
async def delete_post(
    post_id: int,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")
    if post.user_id != user.id:                          # ← 不是自己的文章不能删
        raise HTTPException(status_code=403, detail="只能删除自己的文章")

    await session.delete(post)
    await session.commit()
    return {"message": f"文章 {post_id} 已删除"}


# ============================================================
# GET —— 某篇文章的评论列表（公开）
# ============================================================
@router.get("/{post_id}/comments", response_model=list[CommentOut], summary="文章评论列表")
async def list_comments(
    post_id: int,
    session: AsyncSession = Depends(get_session),
):
    # 先确认文章存在（不存在就不用查评论了）
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    stmt = select(Comment).where(Comment.post_id == post_id).order_by(Comment.id.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


# ============================================================
# POST —— 发评论（需登录，自动绑定用户和文章）
# ============================================================
@router.post("/{post_id}/comments", status_code=201, response_model=CommentOut, summary="发表评论")
async def create_comment(
    post_id: int,
    data: CommentCreate,                                 # 前端只传 content
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    # 确认文章存在
    post = await session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="文章不存在")

    # user_id 和 post_id 都自动绑定，前端不需要传
    comment = Comment(**data.model_dump(), user_id=user.id, post_id=post_id)
    session.add(comment)
    await session.commit()
    await session.refresh(comment)
    return comment
