from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum as EnumSQL
from enum import Enum
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from core.configs import settings
from datetime import datetime
from .baseModel import Base

class Status(str, Enum):
    pending = "Pendente"
    approved = "Aprovado"
    denied_due_lack_stock = "Negado por falta de estoque"
    denied_due_user_limit = "Negado por limite de empréstimos"
    denied_due_user_fines = "Negado por multas pendentes"
    denied = "Negado"

class LoanRequestModel(Base):
    __tablename__ = "solicitacoes_emprestimos"
    
    __variable_name__ = "Solicitação de emprestimo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("livros.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    status = Column(EnumSQL(Status, name="status_solicitacoes"), default=Status.pending)
    changer_by = Column(Integer, ForeignKey("usuarios.id"), nullable=True)

    

    __table_args__ = (
        UniqueConstraint("book_id","user_id", name="uq_book_user_requests"),
    )

from .user_model import UserModel
from .book_model import BookModel
LoanRequestModel.book = relationship(
    "BookModel",
    back_populates="requestLoans"
)
LoanRequestModel.user = relationship(
    "UserModel",
    back_populates="requestLoans",
    foreign_keys=[LoanRequestModel.user_id]
)

    
