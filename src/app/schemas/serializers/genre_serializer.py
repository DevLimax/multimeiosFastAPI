
from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class BooktoGenreSchema(BaseModel):
    id: Optional[int] = None
    title: str
    author: str
    quantity: int

#=======================================
class GenreSchemaBase(BaseModel):
    id: Optional[int] = None
    name: str

    model_config = ConfigDict(
        from_attributes=True
    )
        
class GenreSchemaWithRelations(GenreSchemaBase):
    primary_books: Optional[List[BooktoGenreSchema]] = None
    secondary_books: Optional[List[BooktoGenreSchema]] = None

class GenreSchemaUpdate(GenreSchemaBase):
    name: Optional[str] = None
    
class GenreSchemaCreate(BaseModel):
    name: str
