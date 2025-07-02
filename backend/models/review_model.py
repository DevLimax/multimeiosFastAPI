from sqlalchemy import Column, Integer, String, ForeignKey, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from core.configs import settings
from .baseModel import Base

class BookReview(Base):
    __tablename__ = "avaliacoes"
    
    __variable_name__ = "Avaliação"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("livros.id"), nullable=False) 
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)  
    comment = Column(String(144), nullable=True)
    rating = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("book_id", "user_id", name="uq_book_user_reviews"),
    )

#Relations 

from .book_model import BookModel
from .user_model import UserModel
BookReview.user = relationship(
    "UserModel",  
    back_populates="reviews",
)
BookReview.book = relationship(
    "BookModel",
    back_populates="reviews",
)
