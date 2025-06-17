from sqlalchemy import Column, Integer, String, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from core.configs import settings

class GenreModel(settings.DBBASEMODEL):
    __tablename__ = "generos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(144), nullable=False, unique=True)

