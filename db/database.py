from motor.motor_asyncio import AsyncIOMotorClient
from db.config import settings

CLIENT = AsyncIOMotorClient(settings.mongodb_url)
db = CLIENT[settings.MONGODB_DB]