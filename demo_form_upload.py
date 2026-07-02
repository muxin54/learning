"""
第10课 演示 —— Form 表单 与 文件上传
"""
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse

app = FastAPI(title="第10课 - 表单与文件上传")


# ============================================================
# 一、Form 表单接收
# ============================================================
# 和 JSON 的区别：
#   JSON:   card_in: CardCreate          → Pydantic 模型
#   Form:   username: str = Form()        → 逐个字段声明，用 Form()
#
# 适用场景：传统 HTML <form> 提交、OAuth2 登录表单

@app.post("/login-form")
async def login_with_form(
    username: str = Form(),   # Form() 告诉 FastAPI：从表单数据里取
    password: str = Form(),   # 不是从 JSON body 里取
):
    """模拟表单登录 —— 和 /docs 页面右上角的登录表单一样"""
    # ⚠️ 真实场景密码要加密对比，这里仅演示
    return {
        "message": "表单登录成功",
        "username": username,
        # 密码不返回！实际开发中只返回 token
    }


# ============================================================
# 二、文件上传（单文件）
# ============================================================
# UploadFile 自带文件名、大小、类型，比 bytes 好用
# File() 用于纯字节流（小文件），但一般用 UploadFile

@app.post("/upload/avatar")
async def upload_avatar(file: UploadFile = File()):
    """上传单个头像文件"""
    # UploadFile 对象有哪些属性？
    #   file.filename  → 原始文件名
    #   file.size      → 文件大小（字节）—— ⚠️ 不在属性里，要读完后才知道
    #   file.content_type → MIME 类型，如 image/png

    content = await file.read()  # 读取文件内容
    size = len(content)

    return {
        "message": "上传成功",
        "filename": file.filename,
        "content_type": file.content_type,
        "size": f"{size} bytes ({size/1024:.1f} KB)",
    }


# ============================================================
# 三、文件上传（含额外表单字段）
# ============================================================
# 实际场景：上传头像同时传 user_id 来标识是谁的头像

@app.post("/upload/avatar-with-user")
async def upload_avatar_with_form(
    user_id: int = Form(),              # 表单字段
    file: UploadFile = File(),          # 文件字段
):
    """上传头像，同时传 user_id"""
    content = await file.read()

    return {
        "message": "上传成功",
        "user_id": user_id,
        "filename": file.filename,
        "size": f"{len(content)} bytes",
    }


# ============================================================
# 四、多文件上传
# ============================================================
@app.post("/upload/photos")
async def upload_photos(files: list[UploadFile] = File()):
    """一次上传多张照片"""
    result = []
    for f in files:
        content = await f.read()
        result.append({
            "filename": f.filename,
            "size": len(content),
        })

    return {
        "message": f"共上传 {len(result)} 个文件",
        "files": result,
    }


# ============================================================
# 五、文件保存到磁盘
# ============================================================
import os

UPLOAD_DIR = "uploads"  # 保存目录

@app.post("/upload/save")
async def upload_and_save(file: UploadFile = File()):
    """上传文件并保存到本地磁盘"""
    # 1. 确保目录存在
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # 2. 读取内容
    content = await file.read()

    # 3. 写入文件（真实项目要做文件名去重、安全过滤等处理）
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        f.write(content)

    return {
        "message": "文件已保存",
        "path": save_path,
        "size": len(content),
    }


# ============================================================
# 六、HTML 页面 —— 方便在浏览器里直接测上传
# ============================================================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>第10课 文件上传测试</title></head>
<body>
    <h2>📤 上传头像</h2>
    <form action="/upload/save" method="post" enctype="multipart/form-data">
        <input type="file" name="file"><br><br>
        <button type="submit">上传</button>
    </form>

    <h2>📤 上传头像 + 用户ID</h2>
    <form action="/upload/avatar-with-user" method="post" enctype="multipart/form-data">
        <label>用户ID：</label><input name="user_id"><br><br>
        <input type="file" name="file"><br><br>
        <button type="submit">上传</button>
    </form>

    <h2>📤 多文件上传</h2>
    <form action="/upload/photos" method="post" enctype="multipart/form-data">
        <input type="file" name="files" multiple><br><br>
        <button type="submit">上传</button>
    </form>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def test_page():
    """打开浏览器直接看到上传表单，方便测试"""
    return HTML_PAGE


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
