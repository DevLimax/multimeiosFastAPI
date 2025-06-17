from sqlalchemy import Column, Integer, String, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from core.configs import settings

class BookModel(settings.DBBASEMODEL):
    __tablename__ = "livros"

    id = Column(Integer, autoincrement=True, primary_key=True)
    title = Column(String(50), nullable=False)
    author = Column(String(50), nullable=False)
    synopsis = Column(String(255), nullable=True)
    cover = Column(String(50),default="static/images/bookDefault.png")
    genre = Column(Integer, ForeignKey("generos.id"))
    genre_two = Column(Integer, ForeignKey("generos.id"), nullable=True)
    quantity = Column(Integer, default=0)
    added_by = Column(Integer, ForeignKey("usuarios.id"))