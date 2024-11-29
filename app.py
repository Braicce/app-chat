from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root():
    return FileResponse("static/chat.html")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, username: str):
    await manager.connect(websocket)
    try:
        # Enviar mensagem de boas-vindas sem mostrar "Sistema"
        await manager.broadcast({"sender": "Chat", "message": f"{username} entrou no chat"})
        while True:
            data = await websocket.receive_text()
            await manager.broadcast({"sender": username, "message": data})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({"sender": "Chat", "message": f"{username} saiu do chat"})
        
from fastapi.responses import FileResponse