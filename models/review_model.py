from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from core.configs import settings

class BookReview(settings.DBBASEMODEL):
    __tablename__ = "avaliacoes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book = Column(Integer, ForeignKey("livros.id"))
    user = Column(Integer, ForeignKey("usuarios.id"))
    comment = Column(String(144), nullable=True)
    rating = Column(Float, nullable=False)
    book_details = relationship(
        "BookModel",
        back_populates="reviews",
        lazy="joined"
    )
    
    

    