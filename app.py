from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from datetime import datetime
from typing import List

# Configurar a conexão com o MongoDB
client = MongoClient('mongodb://mongodb:27017/')  # Ajuste o URI conforme necessário
db = client['chat_app']  # Nome do banco de dados
messages_collection = db['messages']  # Nome da coleção

app = FastAPI()

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rota principal
@app.get("/")
def read_root():
    return FileResponse("static/chat.html")

# Gerenciador de conexões
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

# WebSocket para o chat
@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, username: str):
    await manager.connect(websocket)
    try:
        # Enviar histórico de mensagens ao cliente apenas uma vez ao conectar
        previous_messages = list(messages_collection.find().sort("timestamp", 1))
        for msg in previous_messages:
            await websocket.send_json({
                "username": msg.get("username", "Unknown"),  # Nome do usuário
                "message": msg["message"],
                "timestamp": msg["timestamp"].isoformat(),
            })

        # Enviar mensagem de boas-vindas sem mostrar "Sistema"
        await manager.broadcast({"sender": "Chat", "message": f"{username} entrou no chat"})

        # Loop para receber e enviar novas mensagens
        while True:
            data = await websocket.receive_text()
            # Criar mensagem e salvar no banco
            message = {
                "username": username,
                "message": data,
                "timestamp": datetime.now(),
            }
            messages_collection.insert_one(message)
            # Repassar mensagem para todos os conectados
            await manager.broadcast({
                "username": message["username"],
                "message": message["message"],
                "timestamp": message["timestamp"].isoformat(),
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast({"sender": "Chat", "message": f"{username} saiu do chat"})
