
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_get_todos():
    """公开接口：不登录也能查"""
    response = client.get("/todos/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_todo():
    """登录后新增待办"""
    # 先注册（避免用户名已存在，不管成功还是报"已存在"都行）
    client.post("/users/register", json={"username": "testuser", "password": "123456"})
    # 再登录
    login_resp = client.post("/users/login", json={"username": "testuser", "password": "123456"})
    token = login_resp.json()["access_token"]
    # 带着 token 新增
    response = client.post(
        "/todos/",
        json={"title": "测试"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201


def test_get_one_not_found():
    """查不存在的待办 → 404"""
    response = client.get("/todos/99999")
    assert response.status_code == 404


def test_create_without_auth():
    """不登录新增 → 401"""
    response = client.post("/todos/", json={"title": "hack"})
    assert response.status_code == 401

