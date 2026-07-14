# 第26课 演示 —— Docker 镜像构建与运行
import sys

commands = """
=== Docker 常用命令速查 ===

1. 构建镜像（在项目根目录跑）：
   docker build -t card-api .

2. 运行容器：
   docker run -d --name card-api -p 8000:8000 --env-file .env card-api
                            │                │            │         │
                            │                │            │         └── 镜像名
                            │                │            └── 注入环境变量文件
                            │                └── 本机8000 → 容器8000
                            └── 容器名字

3. 看日志：
   docker logs card-api

4. 停止：
   docker stop card-api

5. 删除容器：
   docker rm card-api

6. 进容器内部（调试用）：
   docker exec -it card-api bash

7. 查看运行中的容器：
   docker ps

8. 查看所有容器（包括已停止）：
   docker ps -a

9. 删除镜像：
   docker rmi card-api

=== docker-compose（一键启动 API + 数据库） ===
"""

compose_yaml = '''version: "3.8"
services:
  web:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: fastapi_learning
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
'''

print()
print("=" * 60)
print("🔑 核心理解：")
print("  Docker 镜像 = 一套完整的"操作系统环境包"——Python、依赖、")
print("  你的代码全打包在一起。扔到任何机器上都能跑一样的效果。")
print()
print("  开发机、测试服、生产服 → 同一个镜像 → 行为完全一致")
print("  不会再出现"我这能跑你那不能跑"的情况")
print("=" * 60)

if __name__ == "__main__":
    print(commands)
    print("=== docker-compose.yml（一键启动 API + 数据库） ===")
    print(compose_yaml)
