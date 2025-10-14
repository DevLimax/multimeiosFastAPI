from sqlalchemy import ForeignKey, UniqueConstraint, Enum as EnumSQL
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .base_model import Base
from enum import Enum

class Status(str, Enum):
    pending = "Pendente"
    approved = "Aprovado"
    denied_due_lack_stock = "Negado por falta de estoque"
    denied_due_user_limit = "Negado por limite de empréstimos"
    denied_due_user_fines = "Negado por multas pendentes"
    denied = "Negado"

class LoanRequestModel(Base):
    __tablename__ = "solicitacoes_emprestimos"
    __table_args__ = (
        UniqueConstraint("book_id","user_id", name="uq_book_user_requests"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    book_id = mapped_column(ForeignKey("livros.id"), nullable=False, index=True)
    user_id = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    status = mapped_column(EnumSQL(Status, name="status_solicitacoes"), default=Status.pending, index=True)
    changer_by = mapped_column(ForeignKey("usuarios.id"), nullable=True, index=True)

from .user_model import UserModel
from .book_model import BookModel
LoanRequestModel.book = relationship(
    "BookModel",
    back_populates="requestLoans",
    lazy="joined"
)
LoanRequestModel.user = relationship(
    "UserModel",
    back_populates="requestLoans",
    foreign_keys=[LoanRequestModel.user_id],
    lazy="joined"
)

    