from fastapi import FastAPI

app = FastAPI(
    title="第一个",
    description="基础",
    version="1.0.0"
)


# ============================================
# 第1课已有的接口（保留不动）
# ============================================

@app.get("/")
def root():
    """根路径"""
    return {"message": "hello", "status": "成功启动"}


@app.get("/hello")
def hello():
    """返回问候语"""
    return {"say": "您好"}


@app.get("/info")
def get_info():
    """返回个人信息"""
    return {"name": "mumu", "date": "2026-06-23", "status": "正在学习"}


# ============================================
# 第2课：商品管理接口组（增删改查 + 搜索分页合体）
# ============================================

# 商品数据（第3课升级版：加了 category 和 in_stock 字段）
products = [
    {"id": 1, "name": "Python入门书", "category": "书籍", "price": 59, "in_stock": True},
    {"id": 2, "name": "机械键盘", "category": "外设", "price": 299, "in_stock": True},
    {"id": 3, "name": "显示器", "category": "外设", "price": 1299, "in_stock": False},
    {"id": 4, "name": "Django实战", "category": "书籍", "price": 79, "in_stock": True},
    {"id": 5, "name": "鼠标垫", "category": "外设", "price": 29, "in_stock": True},
    {"id": 6, "name": "FastAPI入门", "category": "书籍", "price": 49, "in_stock": False},
    {"id": 7, "name": "耳机", "category": "外设", "price": 399, "in_stock": True},
]


# ---- 1. GET：查询商品列表（支持搜索 + 过滤 + 分页） ----

@app.get("/products")
def list_products(
    keyword: str = "",        # 搜索关键词，不传就返回全部
    category: str = "",       # 分类筛选，不传就看全部
    min_price: float = 0,     # 最低价格，默认0
    max_price: float = 99999, # 最高价格，默认很大
    in_stock: bool = None,    # 只看有货？ None=不过滤
    page: int = 1,            # 第几页，默认1
    page_size: int = 10,      # 每页几条，默认10
):
    """
    商品列表接口：不带参数 = 返回全部，带参数 = 按条件筛选
    示例：
    - /products                          → 全部商品
    - /products?keyword=键盘             → 搜商品名
    - /products?category=书籍            → 只看书籍
    - /products?min_price=100&max_price=500 → 价格区间
    - /products?in_stock=true            → 只看有货
    - /products?page=2&page_size=3       → 分页
    """
    result = products  # 从全部数据开始

    # 逐条件过滤
    if keyword:
        result = [p for p in result if keyword.lower() in p["name"].lower()]
    if category:
        result = [p for p in result if p["category"] == category]
    result = [p for p in result if min_price <= p["price"] <= max_price]
    if in_stock is not None:
        result = [p for p in result if p["in_stock"] == in_stock]

    # 分页
    total = len(result)
    start = (page - 1) * page_size
    end = start + page_size
    page_data = result[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "data": page_data,
    }


@app.get("/products/categories")
def get_categories():
    """获取所有分类"""
    cats = sorted(set(p["category"] for p in products))
    return {"categories": cats}


# ---- 2. GET：查询单个商品（路径参数） ----

@app.get("/products/{product_id}")
def get_one_product(product_id: int):  # : int 自动把路径字符串转为整数
    """
    获取单个商品详情
    访问示例：http://127.0.0.1:8000/products/1
    """
    for p in products:
        if p["id"] == product_id:
            return p  # 找到了，返回
    return {"error": "商品不存在"}  # 没找到，返回提示


# ---- 3. POST：新增商品 ----

@app.post("/products")
def create_product(
    name: str,
    price: float,
    category: str = "未分类",  # 可选字段，不填默认"未分类"
    in_stock: bool = True,     # 可选字段，不填默认有货
):
    """
    新增一个商品
    在 /docs 页面点 Try it out，填入各项即可测试
    """
    new_id = max(p["id"] for p in products) + 1 if products else 1
    new_product = {
        "id": new_id,
        "name": name,
        "price": price,
        "category": category,
        "in_stock": in_stock,
    }
    products.append(new_product)
    return {"message": "新增成功", "product": new_product}


# ---- 4. PUT：修改商品 ----

@app.put("/products/{product_id}")
def update_product(
    product_id: int,
    name: str,
    price: float,
    category: str = "未分类",
    in_stock: bool = True,
):
    """
    修改某个商品的信息
    """
    for p in products:
        if p["id"] == product_id:
            p["name"] = name
            p["price"] = price
            p["category"] = category
            p["in_stock"] = in_stock
            return {"message": "修改成功", "product": p}
    return {"error": "商品不存在"}


# ---- 5. DELETE：删除商品 ----

@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    """
    删除指定商品
    访问示例：DELETE /products/1
    """
    global products  # 声明要修改外面的 products 变量
    old_len = len(products)
    # 列表推导式：保留所有"不是这个 id"的商品，即过滤掉目标
    products = [p for p in products if p["id"] != product_id]
    if len(products) < old_len:
        return {"message": f"商品 {product_id} 已删除"}
    return {"error": "商品不存在"}



books = [
    {"id": 1, "title": "Python入门书", "author": "张三", "category": "编程", "pages": 350, "price": 59},
    {"id": 2, "title": "三体", "author": "刘慈欣", "category": "科幻", "pages": 580, "price": 68},
    {"id": 3, "title": "活着", "author": "余华", "category": "文学", "pages": 200, "price": 39},
    {"id": 4, "title": "Django实战", "author": "李四", "category": "编程", "pages": 420, "price": 79},
    {"id": 5, "title": "流浪地球", "author": "刘慈欣", "category": "科幻", "pages": 350, "price": 49},
    {"id": 6, "title": "FastAPI入门", "author": "王五", "category": "编程", "pages": 280, "price": 55},
    {"id": 7, "title": "围城", "author": "钱钟书", "category": "文学", "pages": 360, "price": 45},
]


@app.get("/books")
def list_books(
    keyword: str = "",        # 搜书名，模糊匹配
    author: str = "",         # 按作者筛选
    category: str = "",       # 按分类筛选
    min_pages: int = 0,       # 最低页数
    max_pages: int = 99999,   # 最高页数
    page: int = 1,            # 第几页
    page_size: int = 10,      # 每页几条
):
    """图书搜索 + 分页：不带参数 = 全部，带参数 = 筛选"""
    result = books  # 从全部数据开始

    # 关键词搜书名（模糊匹配）
    if keyword:
        result = [i for i in result if keyword.lower() in i["title"].lower()]

    # 按作者筛选
    if author:
        result = [i for i in result if i["author"] == author]

    # 按分类筛选
    if category:
        result = [i for i in result if i["category"] == category]

    # 页数范围
    if min_pages:
        result = [i for i in result if i["pages"] >= min_pages]
    if max_pages:
        result = [i for i in result if i["pages"] <= max_pages]

    # 分页
    total = len(result)                                 # 符合条件的总数
    start = (page - 1) * page_size                      # 起始位置
    end = start + page_size                             # 结束位置
    page_data = result[start:end]                       # 当前页数据

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "data": page_data,
    }


@app.get("/books/categories")
def get_book_categories():
    """获取图书所有分类"""
    cats = sorted(set(i["category"] for i in books))
    return {"categories": cats}


@app.get("/books/{book_id}")
def get_one_book(book_id: int):
    """获取单本图书详情"""
    for i in books:
        if i["id"] == book_id:
            return i  # 找到了，返回
    return {"error": "书籍不存在"}

@app.post("/books")
def create_a_book(
    title: str,               # 书名（必填）
    author: str,               # 作者（必填）
    category: str = "未分类",   # 分类，可选
    pages: int = 0,            # 页数，可选
    price: float = 0,          # 价格，可选
):
    """新增一本书"""
    new_id = max(i["id"] for i in books) + 1 if books else 1
    new_book = {
        "id": new_id,
        "title": title,
        "author": author,
        "category": category,
        "pages": pages,
        "price": price,
    }
    books.append(new_book)
    return {"message": "新增成功", "book": new_book}

@app.put("/books/{book_id}")
def update_a_book(
    book_id: int,
    title: str,               # 书名（必填）
    author: str,               # 作者（必填）
    category: str = "未分类",   # 分类，可选
    pages: int = 0,            # 页数，可选
    price: float = 0,          # 价格，可选
):
    """修改某本书的信息"""
    for i in books:
        if i["id"] == book_id:
            i["title"] = title
            i["author"] = author
            i["category"] = category
            i["pages"] = pages
            i["price"] = price
            return {"message": "修改成功", "book": i}
    return {"error": "书籍不存在"}

@app.delete("/books/{book_id}")
def delete_one_book(book_id:int):
    global books
    old_len=len(books)
    books=[i for i in books if i["id"]!=book_id]
    if len(books)<old_len:
        return {"message": f"书籍 {book_id} 已删除"}
    return {"error": "书籍不存在"}


# ============================================
# 第4课新增：状态码 + 请求体 + 响应控制
# ============================================

from fastapi import HTTPException             # HTTPException：手动抛错误状态码
from pydantic import BaseModel                  # BaseModel：定义请求体的数据格式


# ========== 请求体模型 ==========

class BookCreate(BaseModel):
    """用 Pydantic 模型定义"新增图书"时前端必须传来的数据结构"""
    title: str                                   # 书名，必填
    author: str                                  # 作者，必填
    category: str = "未分类"                      # 分类，选填
    pages: int = 0                               # 页数，选填
    price: float = 0.0                           # 价格，选填


class BookUpdate(BaseModel):
    """用 Pydantic 模型定义"修改图书"时的数据结构（全部字段选填，只改传了的）"""
    title: str | None = None                     # str | None 表示"可以是字符串或空"
    author: str | None = None
    category: str | None = None
    pages: int | None = None
    price: float | None = None


# ========== 使用请求体模型的新接口 ==========

@app.post("/books_v2", status_code=201)           # status_code=201 表示"创建成功"
def create_book_v2(book: BookCreate):
    """
    用 Pydantic 请求体接收数据的方式
    相比老版 POST /books：
    - 所有字段通过 JSON 请求体一次传进来，不用一个个写参数
    - 自动校验：title、author 缺了会直接报错 422
    - 返回 201 状态码：符合 REST 规范
    """
    new_id = max(i["id"] for i in books) + 1 if books else 1
    new_book = book.model_dump()                  # model_dump() 把 Pydantic 对象转成字典
    new_book["id"] = new_id                       # 补上 id 字段
    books.append(new_book)
    return new_book                               # 直接返回新增的书，状态码自动 201


@app.put("/books_v2/{book_id}")
def update_book_v2(book_id: int, book: BookUpdate):
    """
    用 Pydantic 请求体修改图书
    相比老版 PUT /books：
    - 只改传了的字段（model_dump(exclude_unset=True) 去掉了没传的）
    - 加上 HTTPException 返回 404
    """
    for i in books:
        if i["id"] == book_id:
            # exclude_unset=True：只取前端实际传了的字段，没传的不要
            update_data = book.model_dump(exclude_unset=True)
            i.update(update_data)                 # 字典的 update 方法：一次性覆盖多个字段
            return {"message": "修改成功", "book": i}

    raise HTTPException(status_code=404, detail="书籍不存在")
    # ⬆ HTTPException：抛出一个带状态码的错误，前端能据此判断"没找到"


@app.get("/books_v2/{book_id}")
def get_one_book_v2(book_id: int):
    """
    查单本书 —— 用 HTTPException 返回 404
    相比老版：不返回 200 + error 字段，而是直接返回 404 状态码
    """
    for i in books:
        if i["id"] == book_id:
            return i
    raise HTTPException(status_code=404, detail=f"书籍 {book_id} 不存在")

class ProductCreate(BaseModel):
    name: str                                     # 商品名，必填
    price: float = 0                              # 价格，选填
    in_stock: bool = True                         # 有货？默认 True
    category: str = "未分类"                       # 分类，选填（注意拼写：category 不是 categroy）


class ProductUpdate(BaseModel):
    name: str | None = None                       # str | None = 可以是字符串也可以是空
    price: float | None = None
    in_stock: bool | None = None
    category: str | None = None



@app.post("/products_v2", status_code=201)       # status_code 不是 statu_code
def create_product_v2(product: ProductCreate):
    """新增商品 —— Pydantic 请求体版本"""
    new_id = max(p["id"] for p in products) + 1 if products else 1  # 取最大id+1
    new_product = product.model_dump()
    new_product["id"] = new_id
    products.append(new_product)
    return new_product                                     # 返回新增的商品，状态码自动 201


@app.put("/products_v2/{product_id}")
def update_product_v2(product_id: int, product: ProductUpdate):
    """修改商品 —— 只改传了的字段"""
    for p in products:
        if p["id"] == product_id:
            update_data = product.model_dump(exclude_unset=True)  # 注意：model_dump 不是 model_dumps
            p.update(update_data)
            return {"message": "修改成功", "product": p}

    raise HTTPException(status_code=404, detail="商品不存在")

    








information=[
    {"id":1,"name":"wzt","title":"文职","phone":11111,"email":"1qq.com","company":"中大"},
    {"id":2,"name":"lzz","title":"技术","phone":11112,"email":"2qq.com","company":"南山"},
    {"id":3,"name":"xsh","title":"销售","phone":11113,"email":"3qq.com","company":"海洋"},
    {"id":4,"name":"wij","title":"牛马","phone":11114,"email":"4qq.com","company":"中大"},
    ]


@app.get("/person")
def get_all(keyword:str='',page:int=1,page_size:int=10):
    result=information
    if keyword:
        result=[i for i in result if keyword.lower() in i["name"].lower()]


    total=len(result)
    start=(page-1)*page_size
    end=start+page_size
    page_data=result[start:end]

    return {
        "total":total,
        "page_data":page_data,
        "page":page,
        "page_size":page_size
    }

@app.get("/person/{person_id}")
def get_one(person_id:int):
    for i in information:
        if i["id"]==person_id:
            return i
        
    raise HTTPException(status_code=404,detail="找不到个人名片")

class createinformation(BaseModel):

    name:str
    title:str=""
    phone:int=0
    email:str=""

class updateinformation(BaseModel):
    name:str|None=None
    title:str|None=None
    phone:int|None=None
    email:str|None=None



@app.post("/person",status_code=201)
def create_one(infor:createinformation):
    new_id=max(p["id"] for p in information)+1 if information else 1
    new_information=infor.model_dump()
    new_information["id"]=new_id
    information.append(new_information)
    return new_information

@app.put("/person/{person_id}")
def update_one(person_id:int,infor:updateinformation):
    for i in information:
        if i["id"]==person_id:
            update_data=infor.model_dump( exclude_unset=True)
            i.update(update_data)
            return {"message":"更新成功"}
        
    raise HTTPException(status_code=404,detail="更新失败")

@app.delete("/person/{person_id}")
def delete_one(person_id:int):
    global information
    old_len=len(information)
    information=[i for i in information if i["id"] !=person_id]
    if len(information)<old_len:
        return {"message":"删除成功"}
    raise HTTPException(status_code=404,detail="删除失败")









