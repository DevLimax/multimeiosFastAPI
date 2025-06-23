from sqlalchemy import Column, Integer, String, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from core.configs import settings
from .baseModel import Base

class GenreModel(Base):
    __tablename__ = "generos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(144), nullable=False, unique=True)

#Relations - One To Many
from .book_model import BookModel
GenreModel.primary_books = relationship(
    "BookModel",
    cascade="all, delete-orphan",
    foreign_keys="BookModel.genre_id",
    back_populates="genre",
    lazy="joined"
)

GenreModel.secondary_books = relationship(
    "BookModel",
    cascade="all, delete-orphan",
    foreign_keys="BookModel.genre_two_id",
    back_populates="genre_two",
    lazy="joined"
)