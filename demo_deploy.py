"""
第25课 演示 —— 生产环境启动配置
"""
import os

# ============================================================
# 生产环境 vs 开发环境
# ============================================================

# 方式1：开发环境（你现在用的）
# uvicorn app.main:app --reload --port 8001
#   --reload = 代码改了自动重启（编辑代码时用）
#   --port 8001 = 显式指定端口

# 方式2：生产环境（Windows）
# uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
#   --host 0.0.0.0 = 监听所有网络接口（外网能访问）
#   --workers 4 = 开 4 个工作进程（多核 CPU 全用上）
#   --reload 去掉 = 生产不需要热重载

# 方式3：生产环境（Linux + Gunicorn）—— 最推荐
# gunicorn app.main:app \
#   --workers 4 \               # 4 个进程
#   --worker-class uvicorn.workers.UvicornWorker \   # 用 uvicorn 的异步 worker
#   --bind 0.0.0.0:8000 \       # 监听地址
#   --access-logfile - \         # 访问日志输出到控制台
#   --error-logfile -            # 错误日志输出到控制台

# ============================================================
# 生产环境 Checklist
# ============================================================
checklist = """
生产环境部署检查清单：
  □ 1. DEBUG 模式关掉
  □ 2. SECRET_KEY 换成随机生成的强密码（openssl rand -hex 32）
  □ 3. 数据库密码换掉，不在 .env 里用弱密码
  □ 4. CORS allow_origins 改成真正的前端域名（不是 *）
  □ 5. 加上健康检查接口 GET /health
  □ 6. --reload 去掉
  □ 7. workers 数量 ≥ 2（单进程挂了全站瘫痪）
  □ 8. 用 Nginx 做反向代理（静态文件、HTTPS、限流）
"""

print(checklist)
print()
print("=" * 60)
print("🔑 关键理解：")
print("  开发模式 = 方便写代码（热重载、详细报错）")
print("  生产模式 = 稳定 + 快 + 安全（多进程、关调试、防攻击）")
print("  两个模式的代码完全一样，只是启动参数不同！")
print("=" * 60)
