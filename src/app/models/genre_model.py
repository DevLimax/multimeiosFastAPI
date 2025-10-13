from sqlmodel import SQLModel, Field, Relationship
from typing import List
from typing import Optional

from app.models.base_model import BaseModel

class GenreModel(SQLModel, table=True):
    __tablename__ = "generos"
    
    id: Optional[int] = Field(primary_key=True, index=True)
    name: str = Field(nullable=False, max_length=144, unique=True)
    
    books: List["BookModel"] = Relationship(back_populates=["genre", "genre_two"], cascade_delete=True)
    

class GenreSchemaBase(SQLModel, table=False):
    
    id: Optional[int] = None
    name: str
    
class GenreSchemaUpdate(SQLModel, table=False):
    
    name: Optional[str]
    
    