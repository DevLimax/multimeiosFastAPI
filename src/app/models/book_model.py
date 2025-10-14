from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base_model import Base


class BookModel(Base):
    __tablename__ = "livros"
    __table_args__ = (
        UniqueConstraint("title","author", name="uq_title_author_books"),
    )

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False, unique=True)
    author: Mapped[str] = mapped_column(nullable=False)
    synopsis: Mapped[str] = mapped_column(nullable=True)
    cover: Mapped[str] = mapped_column(default="static/images/covers/bookDefault.png")
    genre_id: Mapped[int] = mapped_column(ForeignKey("generos.id"))
    genre_two_id: Mapped[int] = mapped_column(ForeignKey("generos.id"), nullable=True)
    quantity: Mapped[int] = mapped_column(default=0)
    added_by_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))   

#Reations - One to Many
from .loan_model import LoanModel
from .loanRequest_model import LoanRequestModel
from .genre_model import GenreModel
from .review_model import BookReview
from .user_model import UserModel
BookModel.loans = relationship(
    "LoanModel",
    cascade="all, delete-orphan",
    back_populates="book",
    lazy="selectin"
)
BookModel.requestLoans = relationship(
    "LoanRequestModel",
    cascade="all, delete-orphan",
    back_populates="book",
    lazy="selectin"
)
BookModel.reviews = relationship(
    "BookReview",
    cascade="all, delete-orphan",
    back_populates="book",
    lazy="selectin"
)
BookModel.genre = relationship(
    "GenreModel",
    foreign_keys=[BookModel.genre_id],
    back_populates="primary_books",
    lazy="joined"
)
BookModel.genre_two = relationship(
    "GenreModel",
    foreign_keys=[BookModel.genre_two_id],
    back_populates="secondary_books",
    lazy="joined"
)
BookModel.added_by = relationship(
    "UserModel",
    foreign_keys=[BookModel.added_by_id],
    back_populates="added_books",
    lazy="joined"
)