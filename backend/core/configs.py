from typing import List, ClassVar
from pydantic_settings import BaseSettings
from sqlalchemy.ext.declarative import declarative_base

class Settings(BaseSettings):
    """
    Configs gerais da aplicação
    """
    ENV: str = "dev"
    API_V1_STR: str = "/api/v1"
    DB_URL: str = "postgresql+asyncpg://lima:postgres@localhost:5432/multimeios"
    DBBASEMODEL: ClassVar = declarative_base()

    JWT_SECRET: str = "SfpbxcK60Gjlnw4oIX3eO9gNTzdd3w1_1NS5gWqkfKg"
    """
    import secrets
    token: str = secrets.token_urlsafe(32)
    """

    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRED: int = 60 * 24

    class Config: 
        case_sensitive = True

settings: Settings = Settings()