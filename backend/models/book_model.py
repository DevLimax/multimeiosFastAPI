from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from core.configs import settings
from .baseModel import Base


class BookModel(Base):
    __tablename__ = "livros"
    
    __variable_name__ = "Livro"

    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String(50), nullable=False, unique=True)
    author = Column(String(50), nullable=False)
    synopsis = Column(String(255), nullable=True)
    cover = Column(String(50),default="static/images/covers/bookDefault.png")
    genre_id = Column(Integer, ForeignKey("generos.id"))
    genre_two_id = Column(Integer, ForeignKey("generos.id"), nullable=True)
    quantity = Column(Integer, default=0)
    added_by_id = Column(Integer, ForeignKey("usuarios.id"))   

    __table_args__ = (
        UniqueConstraint("title","author", name="uq_title_author_books"),
    )

#Reations - One to Many
from .bookloan_model import BookLoanModel
from .loanRequest_model import LoanRequestModel
from .genre_model import GenreModel
from .review_model import BookReview
from .user_model import UserModel
BookModel.loans = relationship(
    "BookLoanModel",
    cascade="all, delete-orphan",
    back_populates="book",
    lazy="joined"
)
BookModel.requestLoans = relationship(
    "LoanRequestModel",
    cascade="all, delete-orphan",
    back_populates="book",
    lazy="joined"
)
BookModel.reviews = relationship(
    "BookReview",
    cascade="all, delete-orphan",
    back_populates="book",
    lazy="joined"
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
    back_populates="books_added",
    lazy="joined"
)
