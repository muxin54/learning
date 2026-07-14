"""
第23课 演示 —— API 测试入门（pytest + TestClient）
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/hello")
def hello(name: str = "World"):
    return {"message": f"Hello, {name}!"}

@app.post("/items")
def create_item(item: dict):
    return {"id": 1, "name": item["name"]}


# ============================================================
# 不需要启动服务器就能测试！
# ============================================================
client = TestClient(app)

# 测试1：GET 请求
def test_hello():
    response = client.get("/hello", params={"name": "主人"})
    assert response.status_code == 200          # 状态码对吗
    assert response.json() == {"message": "Hello, 主人!"}  # 返回数据对吗

# 测试2：POST 请求
def test_create_item():
    response = client.post("/items", json={"name": "测试物品"})
    assert response.status_code == 200
    assert response.json()["name"] == "测试物品"

# 测试3：验证 422 校验
def test_validation():
    response = client.post("/items", json={})   # 故意少传 name
    assert response.status_code == 422          # 应该返回校验错误


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
