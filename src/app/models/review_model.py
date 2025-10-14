from sqlalchemy import ForeignKey,UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.configs import settings
from .base_model import Base

class BookReview(Base):
    __tablename__ = "avaliacoes"
    __table_args__ = (
        UniqueConstraint("book_id", "user_id", name="uq_book_user_reviews"),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("livros.id"), nullable=False, index=True) 
    user_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)  
    comment: Mapped[str] = mapped_column(nullable=True)
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