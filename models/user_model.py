from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from core.configs import settings
from .baseModel import Base

class UserModel(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(144), nullable=False)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    enrollment = Column(Integer, nullable=True, unique=True)
    email = Column(String(256), index=True, nullable=False, unique=True)
    password = Column(String(256), index=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    profile_image = Column(String(255), default="static/images/profiles/defaultProfile.png")
    last_login = Column(DateTime, nullable=True)

    def __str__(self):
        return self.username

#Relations - One to Many

from .bookloan_model import BookLoanModel
from .review_model import BookReview
from .loanRequest_model import LoanRequestModel
UserModel.loans = relationship(
    "BookLoanModel",
    cascade="all, delete-orphan",
    back_populates="user",
    lazy="joined"
)
UserModel.requestLoans = relationship(
    "LoanRequestModel",
    cascade="all, delete-orphan",
    back_populates="user",
    lazy="joined",
    foreign_keys="[LoanRequestModel.user_id]"
)
UserModel.reviews = relationship(
    "BookReview",
    cascade="all, delete-orphan",
    back_populates="user",
    lazy="joined"
)

    
