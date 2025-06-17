from typing import Optional, List
from pydantic import BaseModel, EmailStr

class BookSchemaBase(BaseModel):
    id: Optional[int] = None
    title: str
    author: str
    synopsis: Optional[str] = None
    cover: Optional[str] = None
    genre: int
    genre_two: Optional[int] = None
    quantity: int
    added_by: int 

    class Config:
        from_attributes = True

class BookSchemaUpdate(BookSchemaBase):
    title: Optional[str] = None
    author: Optional[str] = None
    synopsis: Optional[str] = None
    cover: Optional[str] = None
    genre: Optional[int] = None
    genre_two: Optional[int] = None
    quantity: Optional[int] = None



