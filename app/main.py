from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from datetime import datetime
from typing import List
from app.db.create_collections import criarCollections
from app.db.init_db import init_db
from app.db.config import settings
import shutil
from pathlib import Path

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    await criarCollections()
    await init_db()

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")

# Rota principal
@app.get("/")
def read_root():
    return FileResponse("app/templates/chat.html")

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

# Configurar a conexão com o MongoDB
client = MongoClient(settings.mongodb_url)  # Criar uma instância do MongoClient
db = client[settings.MONGODB_DB]  # Selecionar o banco de dados
messages_collection = db['messages']  # Selecionar a coleção

from fastapi import WebSocket
from datetime import datetime

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket, username: str):
    await manager.connect(websocket)

    try:
        # Enviar histórico de mensagens ao cliente
        previous_messages = list(messages_collection.find().sort("timestamp", 1))
        for msg in previous_messages:
            await websocket.send_json({
                "username": msg.get("username", "Unknown"),
                "message": msg["message"],
                "type": msg.get("type", "text"),  # Inclui o tipo de mensagem (text ou photo)
                "timestamp": msg["timestamp"].isoformat(),
            })

        # Mensagem de boas-vindas
        await manager.broadcast({"sender": "Chat", "message": f"{username} entrou no chat"})

        # Loop principal para receber mensagens
        while True:
            data = await websocket.receive_json()

            # Determinar o tipo de mensagem
            msg_type = data.get("type", "text")
            content = data.get("content", "")

            # Salvar mensagem no banco de dados
            message = {
                "username": username,
                "message": content,
                "type": msg_type,
                "timestamp": datetime.now(),
            }
            messages_collection.insert_one(message)

            # Repassar mensagem para todos os conectados
            await manager.broadcast({
                "username": username,
                "message": content,
                "type": msg_type,
                "timestamp": message["timestamp"].isoformat(),
            })

    except Exception as e:
        print(f"Erro no WebSocket: {e}")
    finally:
        await manager.disconnect(websocket)
        await manager.broadcast({"sender": "Chat", "message": f"{username} saiu do chat"})


UPLOAD_DIR = "uploads"

@app.post("/upload")
async def upload_file(file: UploadFile):
    file_location = f"{UPLOAD_DIR}/{file.filename}"

    # Salvar o arquivo no servidor
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Retornar o caminho do arquivo
    return JSONResponse(content={"filePath": f"/{file_location}"})

async def save_message_to_db(username: str, filename: str):
    message = {
        "username": username,
        "type": "photo",
        "content": filename,
        "timestamp": datetime.utcnow()
    }
    await db.messages.insert_one(message)