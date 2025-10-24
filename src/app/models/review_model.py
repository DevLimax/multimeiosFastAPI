from sqlalchemy import ForeignKey,UniqueConstraint, BigInteger, String
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.configs import settings
from .base_model import Base

class BookReview(Base):
    __tablename__ = "avaliacoes"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True)
    book_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("livros.id"), nullable=False, index=True) 
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("usuarios.id"), nullable=False, index=True)  
    comment: Mapped[str] = mapped_column(String(400), nullable=True)
    rating: Mapped[int] = mapped_column(nullable=False, index=True)

#Relations 

from .book_model import BookModel
from .user_model import UserModel
BookReview.user = relationship(
    "UserModel",  
    back_populates="reviews",
    lazy="joined"
)
BookReview.book = relationship(
    "BookModel",
    back_populates="reviews",
    lazy="joined"
)