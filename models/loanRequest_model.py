from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum as EnumSQL
from enum import Enum
from sqlalchemy.orm import relationship
from core.configs import settings
from datetime import datetime

class Status(str, Enum):
    pending = "Pendente"
    approved = "Aprovado"
    denied = "Negado"


class LoanRequestModel(settings.DBBASEMODEL):
    __tablename__ = "solicitaçções de empretimos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now())
    book = Column(Integer, ForeignKey("livros.id"), nullable=False)
    user = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    status = Column(EnumSQL(Status), default=Status.pending)
    changer_by = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    
