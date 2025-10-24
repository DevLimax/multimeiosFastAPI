from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import Base

class GenreModel(Base):
    __tablename__ = "generos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True)
    name: Mapped[str] = mapped_column(String(144), nullable=False, unique=True)

#Relations - One To Many
from .book_model import BookModel
GenreModel.primary_books = relationship(
    "BookModel",
    cascade="all, delete-orphan",
    foreign_keys="BookModel.genre_id",
    back_populates="genre",
    lazy="selectin"
)

GenreModel.secondary_books = relationship(
    "BookModel",
    cascade="all, delete-orphan",
    foreign_keys="BookModel.genre_two_id",
    back_populates="genre_two",
    lazy="selectin"
)