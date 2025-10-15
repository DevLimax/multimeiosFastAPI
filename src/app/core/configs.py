from typing import List, ClassVar
from sqlalchemy.ext.declarative import declarative_base
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    
    ENV: str = "dev"
    API_V1_STR: str = "/api/v1"
    DB_URL: str = "postgresql+asyncpg://lima:postgres@localhost:5432/multimeios"
    DBBASEMODEL: ClassVar = declarative_base()
    
    JWT_SECRET_KEY: str = "d6e86db996a6b8a8427402925eab49761e0b1f9a4f86372ebd179af78b764ec2"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRED: int = 60 * 24

    class Config:
        case_sensitive = True

settings: Settings = Settings()