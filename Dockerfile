# ============================================================
# Dockerfile —— 把项目打包成 Docker 镜像的"菜谱"
# ============================================================
# 每一行 FROM/COPY/RUN 是一层（layer），层层叠加
#
#                         最终镜像
#                        ┌──────────┐
#                   ─ ─ ─│  CMD     │ ← 启动命令
#                        │  COPY .  │ ← 你的代码
#                        │  RUN pip │ ← 安装依赖
#                        │  FROM    │ ← Python 基础镜像
#                        └──────────┘

# ① 用官方 Python 3.11 做基础（已经装好 Python、pip）
FROM python:3.11-slim

# ② 在容器里创建项目目录
WORKDIR /app

# ③ 先复制依赖清单（利用缓存，代码改了不用重装 pip）
COPY requirements.txt .

# ④ 安装依赖
RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# ⑤ 复制项目代码
COPY . .

# ⑥ 暴露端口
EXPOSE 8000

# ⑦ 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
