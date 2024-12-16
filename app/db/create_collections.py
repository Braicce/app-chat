from app.db.config import settings
from app.db.database import CLIENT
import random

database = CLIENT[settings.MONGODB_DB]

async def criarCollections():

    existing_collections = await database.list_collection_names()
    
    if "messages" not in existing_collections:
        await database.create_collection("messages")
        print("A coleção 'chat_app' foi criada e populada com sucesso!")         