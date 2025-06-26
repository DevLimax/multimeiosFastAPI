from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_serializer
from datetime import datetime

class GenreSchemaBase(BaseModel):
    id: Optional[int] = None
    name: str
    created_at: Optional[datetime] = None

    @field_serializer("created_at", when_used="always")
    def serialize_datetime(self, value: Optional[str]) -> Optional[str]:
        if value:
            return value.strftime("%d/%m/%Y %H:%M")
        return None

    class config: 
        from_attributes = True

class GenreSchemaUpdate(GenreSchemaBase):
    name: Optional[str] = None
    
class GenreSchemaCreate(BaseModel):
    name: str

