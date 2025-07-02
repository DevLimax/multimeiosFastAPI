from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_serializer
from datetime import datetime

class GenreSchemaBase(BaseModel):
    id: Optional[int] = None
    name: str
    created_at: datetime
    is_active: bool

    class config: 
        from_attributes = True

class GenreSchemaCreate(BaseModel):
    name: str

class GenreSchemaUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    
