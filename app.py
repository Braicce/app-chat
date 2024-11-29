from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import json

app = FastAPI()

# Lista para armazenar todos os websockets conectados
active_connections: List[WebSocket] = []

# Serve arquivos estáticos (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Rota para retornar o chat.html
@app.get("/")
async def get():
    return HTMLResponse(content=open("static/chat.html").read(), status_code=200)

# WebSocket para o chat
@app.websocket("/ws/chat/lobby")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)  # Convertendo a mensagem recebida
            nickname = message_data.get("nickname", "Desconhecido")
            message = message_data.get("message", "")

            # Enviar a mensagem para todos os usuários conectados
            for connection in active_connections:
                if connection != websocket:
                    # Envia a mensagem com nickname e o texto
                    await connection.send_text(json.dumps({
                        "nickname": nickname,
                        "message": message
                    }))
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        await websocket.close()
