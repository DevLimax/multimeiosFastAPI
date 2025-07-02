from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Enum as EnumSQL
from enum import Enum
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship
from core.configs import settings
from datetime import datetime, timedelta
from .baseModel import Base

class Status(str, Enum):
    awaiting_withdrawal = "Aguardando retirada"
    awaiting_return = "Aguardando devolução"
    returned = "Devolvido"
    returned_after_the_deadline = "Devolvido fora do prazo"
    not_returned = "Não devolvido"
    canceled = "Cancelado"
    lost = "Perdido"

    

class BookLoanModel(Base):
    __tablename__ = "emprestimos"
    
    __variable_name__ = "Emprestimo"

    id = Column(Integer, primary_key=True, autoincrement=True)
    book_id = Column(Integer, ForeignKey("livros.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    status = Column(EnumSQL(Status, name="status_emprestimos"), default=Status.awaiting_withdrawal)
    book_code = Column(String(20), nullable=False)
    loan_date = Column(DateTime, nullable=True)
    return_date = Column(DateTime, nullable=True)

    __table_args__ = (
        UniqueConstraint("book_id","user_id", name="uq_book_user_loans"),
    )

#Relations
from .user_model import UserModel
from .book_model import BookModel
BookLoanModel.book = relationship(
    "BookModel",
    back_populates="loans",
    lazy="joined"
)
BookLoanModel.user = relationship(
    "UserModel",
    back_populates="loans",
    lazy="joined"
)








