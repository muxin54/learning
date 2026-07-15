"""
ADV-1 演示 —— WebSocket 原理
直接运行：python demo_websocket.py
然后用浏览器打开 http://127.0.0.1:8000 看效果
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="ADV-1 - WebSocket 入门")

# 保存所有在线的 WebSocket 连接
connected_clients: list[WebSocket] = []


# ============================================================
# 一、最简 WebSocket 端点
# ============================================================
@app.websocket("/ws/echo")                        # ← @app.websocket 不是 @app.get！
async def echo(websocket: WebSocket):             # ← 参数是 WebSocket 对象
    """回声服务器：收到什么就回什么"""
    await websocket.accept()                      # ① 接受连接（握手）
    try:
        while True:                               # ② 无限循环，保持连接
            data = await websocket.receive_text() # ③ 等客户端发消息（阻塞）
            await websocket.send_text(f"你说了: {data}")  # ④ 回复
    except WebSocketDisconnect:                   # ⑤ 客户端断开
        print("客户端断开了")


# ============================================================
# 二、聊天室 —— 广播模式
# ============================================================
@app.websocket("/ws/chat")
async def chat(websocket: WebSocket):
    """聊天室：一个人发消息，所有人收到"""
    await websocket.accept()
    connected_clients.append(websocket)            # 加入聊天室

    try:
        while True:
            data = await websocket.receive_text()
            # 广播给所有人
            for client in connected_clients:
                await client.send_text(data)
    except WebSocketDisconnect:
        connected_clients.remove(websocket)        # 离开时移除


# ============================================================
# 三、HTML 测试页面（在浏览器里直接聊天）
# ============================================================
HTML = """
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>WebSocket 聊天测试</title></head>
<body>
    <h2>💬 简易聊天室</h2>
    <input id="msg" placeholder="输入消息……" style="width:300px">
    <button onclick="send()">发送</button>
    <hr>
    <div id="chat"></div>

    <script>
        // 连接 WebSocket（换成 /ws/echo 就是回声模式）
        const ws = new WebSocket("ws://127.0.0.1:8000/ws/chat");
        const chat = document.getElementById("chat");

        ws.onmessage = (e) => {
            chat.innerHTML += "<p>" + e.data + "</p>";   // 收到消息显示出来
        };
        ws.onopen = () => chat.innerHTML += "<p>✅ 已连接</p>";
        ws.onclose = () => chat.innerHTML += "<p>❌ 已断开</p>";

        function send() {
            const input = document.getElementById("msg");
            ws.send(input.value);                         // 发送消息
            input.value = "";
        }
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def test_page():
    return HTML


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
