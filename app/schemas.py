"""
schemas.py —— Pydantic 模型（定义接口收什么、返回什么）
"""
from pydantic import BaseModel,Field
from datetime import datetime


# ============================================
# 名片相关
# ============================================

class CardOut(BaseModel):
    id:int
    name:str
    title:str
    phone:str
    email:str
    company:str
    model_config = {"from_attributes": True}
    
class CardListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    data: list[CardOut]



class CardCreate(BaseModel):
    """创建名片时，前端要传的字段"""
    name: str=Field(min_length=1,max_length=50)
    title: str = ""
    phone: str = Field(pattern=r"^(\d{11})?$",default="",description="十一位手机号")
    email: str = Field(pattern=r"^([\w\.-]+@[\w\.-]+\.\w+)?$",default="",description="你的邮箱")
    company: str = ""


class CardUpdate(BaseModel):
    """修改名片时，前端要传的字段（全部可选）"""
    name: str | None = None
    title: str | None = None
    phone: str | None = None
    email: str | None = None
    company: str | None = None


# ============================================
# 用户认证相关
# ============================================
class UserRegister(BaseModel):
    """注册时要传的字段"""
    username: str
    password: str


class UserLogin(BaseModel):
    """登录时要传的字段"""
    username: str
    password: str


class UserResponse(BaseModel):
    """返回给前端的用户信息（绝对不能包含密码！）"""
    id: int
    username: str




#Todo
class TodoCreate(BaseModel):
    title:str

class TodoUpdate(BaseModel):
    title:str|None=None
    done:bool|None=None

class TodoOut(BaseModel):
    id:int
    title:str
    done:bool
    created_at:datetime
    model_config= {"from_attributes": True}


class PostCreate(BaseModel):
    title: str
    content: str


class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class PostOut(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    created_at: datetime
    model_config = {"from_attributes": True}


class CommentCreate(BaseModel):
    content: str


class CommentOut(BaseModel):
    id: int
    content: str
    post_id: int
    user_id: int
    created_at: datetime
    model_config = {"from_attributes": True}
    model_config = {"from_attributes": True}

