import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_USER: str = os.getenv("MONGODB_USER", "admin") #Inserir o seu usuário de banco
    MONGODB_PASSWORD: str = os.getenv("MONGODB_PASSWORD", "password") #Inserir a senha do seu usário de banco
    MONGODB_HOST: str = os.getenv("MONGODB_HOST", "mongodb") #Inserir o IP ou caminho do banco de dados
    MONGODB_PORT: int = int(os.getenv("MONGODB_PORT", 27017)) # Porta utilizada no banco 
    MONGODB_DB: str = os.getenv("MONGODB_DB", "chat_app") # nome da coleção do banco 

    @property
    def mongodb_url(self) -> str:
        return f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}?authSource=admin"

settings = Settings()