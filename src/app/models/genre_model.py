from sqlmodel import SQLModel, Field, Relationship
from typing import List
from typing import Optional

from app.models.base_model import BaseModel

class GenreModel(SQLModel, table=True):
    __tablename__ = "generos"
    
    id: Optional[int] = Field(primary_key=True, index=True)
    name: str = Field(nullable=False, max_length=144, unique=True)
    
    books: List["BookModel"] = Relationship(back_populates="genre", cascade_delete=True)

    def validate_data(self):
        if isinstance(self.id, int) and self.id < 1:
            raise ValueError("ID invalido!")

        if self.name:
            self.name = self.name.lower()
    

class GenreSchemaBase(SQLModel, table=False):
    
    id: Optional[int] = None
    name: str
    
class GenreSchemaUpdate(SQLModel, table=False):
    
    name: Optional[str]
    
    