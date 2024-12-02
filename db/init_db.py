from motor.motor_asyncio import AsyncIOMotorClient
from db.database import settings

async def init_db():
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[settings.MONGODB_DB]

    # Criar banco de dados
    db = client["chat_app"]

    # Fechar a conexão
    client.close()