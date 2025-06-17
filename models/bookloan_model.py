from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum as EnumSQL
from enum import Enum
from sqlalchemy.orm import relationship
from core.configs import settings
from datetime import datetime, timedelta

class Status(str, Enum):
    awaiting_withdrawal = "Aguardando retirada"
    withdrawal_made = "Retirada Feita"
    awaiting_return = "Aguardando devolução"
    returned = "Devolvido"
    returned_after_the_deadline = "Devolvido fora do prazo"
    not_returned = "Não devolvido"
    canceled = "Cancelado"

class BookLoanModel(settings.DBBASEMODEL):
    __tablename__ = "Emprestimos"
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    updated_at = Column(DateTime, nullable=False, default=datetime.now())
    book = Column(Integer, ForeignKey("livros.id"), nullable=False)
    user = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    status = Column(EnumSQL(Status), default=Status.awaiting_withdrawal)
    loan_date = Column(DateTime, default=datetime.now())
    return_date = Column(DateTime, default=datetime.now() + timedelta(days=25))





