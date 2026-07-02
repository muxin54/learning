"""
第8课 演示 —— 嵌套模型 & Field 校验
"""
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr

app = FastAPI(title="第8课 - Field 校验 & 嵌套模型")


# ============================================================
# 一、Field —— 字段校验（每个字段都能加"规矩"）
# ============================================================
# 以前：name: str
# 现在：name: str = Field(min_length=1, max_length=20, description="用户名")
#
# Field 就是"给字段定规矩"，常用参数：

class UserCreate(BaseModel):
    """用户注册 —— 带 Field 校验"""
    username: str = Field(
        min_length=2,                  # 最少2个字
        max_length=20,                 # 最多20个字
        description="用户名",          # Swagger 文档里显示
        examples=["张三"],             # Swagger 示例
    )
    password: str = Field(
        min_length=6,                  # 密码至少6位
        max_length=50,
        description="登录密码",
        examples=["123456"],
    )
    age: int = Field(
        ge=0,                          # greater than or equal → ≥0
        le=150,                        # less than or equal → ≤150
        description="年龄",
        examples=[25],
    )
    email: str = Field(
        pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",  # 正则：必须像邮箱格式
        description="电子邮箱",
        examples=["zhangsan@example.com"],
    )
    score: float = Field(
        gt=0.0,                        # greater than → >0（不含0）
        lt=100.0,                      # less than → <100
        description="分数（0-100）",
        examples=[85.5],
    )


# ============================================================
# 二、嵌套模型 —— 模型套模型
# ============================================================
# 场景：一个用户有多张名片、一个订单有收件人地址

class Address(BaseModel):
    """地址（被嵌套的子模型）"""
    province: str = Field(description="省份")
    city: str = Field(description="城市")
    street: str = Field(description="街道")
    zip_code: str = Field(min_length=6, max_length=6, description="邮编")


class Company(BaseModel):
    """公司信息（被嵌套的子模型）"""
    name: str = Field(min_length=1, description="公司名称")
    address: Address                     # 嵌套！一个 Address 对象
    employee_count: int = Field(ge=0, description="员工数")


class EmployeeCreate(BaseModel):
    """员工注册 —— 嵌套了公司和地址"""
    name: str = Field(min_length=2, max_length=20)
    title: str = ""                     # 没加 Field 也行，自由组合
    company: Company                     # 嵌套整个 Company 对象
    tags: list[str] = []                # 字符串列表


# ============================================================
# 三、综合示例：列表嵌套
# ============================================================
class OrderItem(BaseModel):
    """订单里的一个商品"""
    product_name: str
    quantity: int = Field(ge=1)
    price: float = Field(gt=0)


class Order(BaseModel):
    """一个订单：包含多个商品（列表嵌套）"""
    customer_name: str
    items: list[OrderItem]               # 列表套模型！
    note: str = ""


# ============================================================
# 接口
# ============================================================
@app.post("/users", response_model=UserCreate)
def create_user(user: UserCreate):
    """创建用户 —— 校验规则全在 UserCreate 模型里"""
    return user  # 校验通过才会走到这里，不通过自动返回 422


@app.post("/employees")
def create_employee(emp: EmployeeCreate):
    """创建员工 —— 传 JSON 时 company 必须包含 address！"""
    return {
        "message": "创建成功",
        "employee": emp.model_dump(),
    }


@app.post("/orders")
def create_order(order: Order):
    """创建订单 —— items 是数组，每个元素都要符合 OrderItem"""
    total = sum(item.price * item.quantity for item in order.items)
    return {
        "message": "订单创建成功",
        "total": total,
        "order": order.model_dump(),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
