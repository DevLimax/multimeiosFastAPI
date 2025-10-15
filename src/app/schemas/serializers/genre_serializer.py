
from typing import Optional, List
from pydantic import BaseModel, field_serializer
from datetime import datetime

class BooktoGenreSchema(BaseModel):
    id: Optional[int] = None
    title: str
    author: str
    quantity: int

#=======================================
class GenreSchemaBase(BaseModel):
    id: Optional[int] = None
    name: str

    class config: 
        from_attributes = True
        
class GenreSchemaWithRelations(GenreSchemaBase):
    primary_books: Optional[List[BooktoGenreSchema]] = None
    secondary_books: Optional[List[BooktoGenreSchema]] = None

class GenreSchemaUpdate(GenreSchemaBase):
    name: Optional[str] = None
    
class GenreSchemaCreate(BaseModel):
    name: str
