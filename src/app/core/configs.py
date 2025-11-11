from typing import List, ClassVar
from sqlalchemy.orm import declarative_base
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
import os

class Settings(BaseSettings):
    
    ENV: str = "dev"
    os.getenv("DB_URL", "postgresql+asyncpg://lima:postgres@localhost:5432/multimeios")
    os.getenv("DB_TEST", "false" in ("true", "yes"))
    API_V1_STR: str = "/api/v1"
    DB_URL: str = "postgresql+asyncpg://limadev:postgres@localhost:5432/multimeios"
    DBBASEMODEL: ClassVar = declarative_base()
    
    JWT_SECRET_KEY: str = "d6e86db996a6b8a8427402925eab49761e0b1f9a4f86372ebd179af78b764ec2"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRED: int = 60 * 24

    model_config = ConfigDict(
        case_sensitive = False
    )
    
    #Configurações de E-mail
    SENDER_EMAIL: str = "jpbarroslima12@gmail.com"
    APP_PASSWORD: str = "eeyt rdai mbvd jpgb"
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

settings: Settings = Settings()