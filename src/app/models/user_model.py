from sqlalchemy import String, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.configs import settings
from .base_model import Base
from datetime import datetime

class UserModel(Base):
    __tablename__ = "usuarios"
    
    __variable_name__ = "Usuário"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[str] = mapped_column(nullable=False)
    enrollment: Mapped[int] = mapped_column(nullable=True, unique=True, index=True)
    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(nullable=False)
    is_admin: Mapped[bool] = mapped_column(default=False)
    profile_image: Mapped[str] = mapped_column(default="static/images/profiles/defaultProfile.png")
    last_login: Mapped[datetime] = mapped_column(nullable=True)

    def __str__(self):
        return self.username

#Relations - One to Many
from .loan_model import LoanModel
from .review_model import BookReview
from .loanRequest_model import LoanRequestModel
from .book_model import BookModel
UserModel.loans = relationship(
    "LoanModel",
    cascade="all, delete-orphan",
    back_populates="user",
    lazy="selectin"
)
UserModel.requestLoans = relationship(
    "LoanRequestModel",
    cascade="all, delete-orphan",
    back_populates="user",
    lazy="selectin",
    foreign_keys="[LoanRequestModel.user_id]"
)
UserModel.reviews = relationship(
    "BookReview",
    cascade="all, delete-orphan",
    back_populates="user",
    lazy="selectin"
)
UserModel.added_books = relationship(
    "BookModel",
    cascade="all, delete-orphan",
    back_populates="added_by",
    lazy="selectin"
)

    