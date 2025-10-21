from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class GenreSchemaBase(BaseModel):
    id: Optional[int] = None
    name: str
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class GenreSchemaUpdate(GenreSchemaBase):
    name: Optional[str] = None
    
class GenreSchemaCreate(BaseModel):
    name: str

