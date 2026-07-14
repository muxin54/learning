"""
第18课 演示 —— Depends 依赖注入深入
"""
from fastapi import FastAPI, Depends, HTTPException, Query

app = FastAPI(title="第18课 - 依赖注入深入")


# ============================================================
# 一、带参数的依赖 —— 同一个函数，不同配置
# ============================================================
# 场景：有些接口只允许管理员，有些允许普通用户。角色不同，但校验逻辑一样。

def require_role(role: str):  # ← 注意：这是普通函数，不是依赖！
    """返回一个依赖函数（闭包）"""
    async def check_role():
        """真正干活的依赖函数"""
        # 模拟：从数据库查出来的当前用户角色
        current_user_role = "admin"  # 假装是 admin
        if current_user_role != role:
            raise HTTPException(
                status_code=403,
                detail=f"权限不足，需要 {role} 角色"
            )
        return current_user_role
    return check_role  # 返回一个函数！


@app.get("/admin/dashboard")
async def admin_dashboard(
    role: str = Depends(require_role("admin"))  # ← 传参！require_role("admin") 返回一个依赖
):
    """只有 admin 能访问"""
    return {"message": "管理员面板", "role": role}


@app.get("/user/profile")
async def user_profile(
    role: str = Depends(require_role("user"))    # ← 同一个工厂，不同参数
):
    """user 就能访问"""
    return {"message": "用户个人信息", "role": role}


# ============================================================
# 二、带查询参数的依赖 —— 依赖自己也有参数
# ============================================================
# 场景：分页逻辑到处都要用，写成依赖一次复用

async def pagination(
    page: int = Query(1, ge=1),          # 依赖自身也能声明参数！
    page_size: int = Query(10, ge=1, le=100),
):
    """通用的分页依赖 —— 任何接口加上它就能分页"""
    return {
        "page": page,
        "page_size": page_size,
        "offset": (page - 1) * page_size,
    }


@app.get("/items")
async def list_items(p: dict = Depends(pagination)):
    """分页查物品——分页逻辑不用重复写"""
    return {
        "message": "物品列表",
        "page": p["page"],
        "page_size": p["page_size"],
    }


@app.get("/users")
async def list_users(p: dict = Depends(pagination)):
    """分页查用户——同一个依赖复用！"""
    return {
        "message": "用户列表",
        "page": p["page"],
        "page_size": p["page_size"],
    }


# ============================================================
# 三、类作为依赖 —— 最推荐的写法（可配置 + 有状态）
# ============================================================
# 当依赖逻辑复杂时（比如需要配置、需要初始化），用类比函数更优雅

class PermissionChecker:
    """权限检查器：不同接口实例化不同的检查规则"""

    def __init__(self, required_permission: str):
        self.required_permission = required_permission  # 初始化时绑定权限名

    async def __call__(self) -> str:  # ← __call__ 让对象能当函数用
        """被 Depends 调用时执行这个方法"""
        # 假装从 JWT Token 里解析出来的权限列表
        current_permissions = ["read", "write"]  # 模拟数据

        if self.required_permission not in current_permissions:
            raise HTTPException(
                status_code=403,
                detail=f"你没有 {self.required_permission} 权限"
            )
        return self.required_permission
    #       ↑ __init__ 传参初始化  →  Depends 调用 __call__ → 返回校验结果


@app.get("/documents/read")
async def read_docs(
    perm: str = Depends(PermissionChecker("read"))   # ← 类名(参数) → 自动调 __call__
):
    return {"message": "读取文档", "permission": perm}


@app.get("/documents/write")
async def write_docs(
    perm: str = Depends(PermissionChecker("write"))  # ← 不同参数，同个类
):
    return {"message": "写入文档", "permission": perm}


# ============================================================
# 四、依赖链 —— 层层嵌套
# ============================================================
# 实际项目里：接口 → 鉴权 → 查用户 → 查数据库，一环套一环

async def get_session():
    """最底层：模拟拿数据库连接"""
    return "DB连接"


async def get_current_user():
    """中间层：模拟解析 token 拿用户"""
    return {"id": 1, "username": "张三"}


async def get_user_profile(
    session=Depends(get_session),      # ← 先拿数据库连接
    user=Depends(get_current_user),    # ← 再拿当前用户
):
    """最顶层：合并两个依赖的结果"""
    return {
        "user": user,
        "session": session,
        "profile": f"{user['username']}的详细资料",
    }


@app.get("/me/full")
async def full_profile(profile: dict = Depends(get_user_profile)):
    """依赖链自动装配：get_user_profile → get_session + get_current_user"""
    return profile


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
