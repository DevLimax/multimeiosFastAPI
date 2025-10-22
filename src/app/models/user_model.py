from sqlalchemy import DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.configs import settings
from .base_model import Base
from datetime import datetime, timedelta, timezone
from random import randint

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
    
    #Colunas utilizadas apenas para a verificação do Email
    is_active: Mapped[bool] = mapped_column(default=False) # A coluna so irá ficar True quando o usuário confirmar o email
    verification_code: Mapped[str] = mapped_column(nullable=True)
    verification_code_expiration: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    def __str__(self):
        return self.username
    
    async def generate_verification_code(self):
        self.verification_code = str(randint(100000, 999999))
        self.verification_code_expiration = datetime.now(timezone.utc) + timedelta(minutes=5)
        
    def check_verification_code(self, code) -> bool:
        if self.verification_code == code and self.verification_code_expiration > datetime.now(timezone.utc):
            return True
        
        return False        

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

    