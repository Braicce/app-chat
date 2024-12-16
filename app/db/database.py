from motor.motor_asyncio import AsyncIOMotorClient
from app.db.config import settings

CLIENT = AsyncIOMotorClient(settings.mongodb_url)
db = CLIENT[settings.MONGODB_DB]