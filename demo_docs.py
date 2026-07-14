"""
第24课 演示 —— API 文档进阶
"""
from fastapi import FastAPI


# ① tags_metadata —— 给分组加描述
tags_metadata = [
    {
        "name": "名片管理",
        "description": "名片 CRUD 增删改查，支持搜索和分页。",
    },
    {
        "name": "待办事项",
        "description": "个人待办清单，支持完成/未完成过滤。",
    },
]

# ② 创建 app 时传 tags 元数据
app = FastAPI(
    title="名片管理系统",
    description="一个管理个人名片和待办事项的后端 API。",
    version="6.0.0",
    openapi_tags=tags_metadata,   # ← 分组信息
)


# ============================================================
# ③ 接口上可以加这些来丰富文档
# ============================================================
@app.get(
    "/cards",
    summary="获取名片列表",
    description="支持按姓名、公司模糊搜索，支持分页。",
    response_description="包含 total、page、data 的分页结果",
    tags=["名片管理"],
)
def list_cards():
    """（这个 docstring 只在代码里看，Swagger 看 summary）"""
    return {"total": 0, "data": []}


@app.post(
    "/cards",
    status_code=201,
    summary="新增名片",
    description="所有字段校验通过后写入数据库。",
    tags=["名片管理"],
    deprecated=False,    # True 的话会显示"已弃用"提示
)
def create_card():
    return {"message": "演示"}


# ④ 故意标一个弃用的接口
@app.get(
    "/old-api",
    deprecated=True,     # ← Swagger 里灰色划线，告诉前端别用了
    tags=["名片管理"],
)
def old_api():
    return {"message": "这个接口即将废弃"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
