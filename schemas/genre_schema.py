from typing import Optional, List
from pydantic import BaseModel, EmailStr

class GenreSchemaBase(BaseModel):
    id: Optional[int] = None
    name: str

    class config: 
        from_attributes = True

class GenreSchemaUpdate(GenreSchemaBase):
    name: Optional[str] = None

