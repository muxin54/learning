"""
models.py —— ORM 模型（数据库表的 Python 映射）
一张表 = 一个类
"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, func
from app.database import Base



class Card(Base):
    """
    名片表
    一张表 = 一个类，一个字段 = 一个属性
    """
    __tablename__ = "cards"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)         # 姓名，不能为空
    title = Column(String(100), default="")           # 职位
    phone = Column(String(20), default="")            # 电话
    email = Column(String(100), default="")           # 邮箱
    company = Column(String(100), default="")         # 公司

    def __repr__(self):
        """打印对象时友好显示（调试用）"""
        return f"<Card(id={self.id}, name='{self.name}', title='{self.title}')>"


class User(Base):
    """
    用户表
    只有三个字段：
      id       → 自增主键
      username → 登录账号（唯一，不能重复）
      password → 加密后的密码（永远不存明文！）
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False, unique=True)  # unique=True → 不允许重名
    password = Column(String(200), nullable=False)              # 存的是加密后的哈希值

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class Todo(Base):
    __tablename__="todo"
    id=Column(Integer,primary_key=True,autoincrement=True)
    title=Column(String(200),nullable=False)
    done=Column(Boolean,default=False)
    created_at=Column(DateTime,default=func.now())

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())


class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(String(500), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())