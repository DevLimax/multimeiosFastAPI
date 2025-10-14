from sqlmodel import SQLModel, Relationship, Field, UniqueConstraint
from typing import Optional

from app.models.base_model import BaseModel

class BookModel(SQLModel, table=True):
    __tablename__ = "livros"
    
    __table_args__ = (
        UniqueConstraint("title", "author", name="uq_title_author"),
    )
    
    id: Optional[int] = Field(primary_key=True, index=True)
    title: str = Field(nullable=False, max_length=144, unique=True)
    author: str = Field(nullable=False, max_length=144)
    synopsis: str = Field(nullable=True, max_length=200)
    cover: str = Field(max_length=200, default="static/images/covers/bookDefault.png")
    genre_id: int = Field(nullable=False, foreign_key="generos.id")
    genre_two: Optional[int] = Field(nullable=True, foreign_key="generos.id")
    available_quantity: Optional[int] = Field(nullable=False, default=1)
    added_by_id: int = Field(nullable=False, foreign_key="usuarios.id")
    
    genre: "GenreModel" = Relationship(back_populates="books")
    genre_two: "GenreModel" = Relationship(back_populates="books")
    added_by: "UserModel" = Relationship(back_populates="books_added")
    