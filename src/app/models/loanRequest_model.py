from sqlalchemy import ForeignKey, UniqueConstraint, Enum as EnumSQL, Index, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .base_model import Base
from enum import Enum

class Status(str, Enum):
    pending = "pendente"
    approved = "aprovado"
    denied_due_lack_stock = "negado por falta de estoque"
    denied_due_user_limit = "negado por limite de empréstimos"
    denied_due_user_fines = "negado por multas pendentes"
    denied = "negado"

class LoanRequestModel(Base):
    __tablename__ = "solicitacoes_emprestimos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True)
    book_id = mapped_column(BigInteger, ForeignKey("livros.id"), nullable=False, index=True)
    user_id = mapped_column(BigInteger, ForeignKey("usuarios.id"), nullable=False, index=True)
    status = mapped_column(EnumSQL(Status, name="status_solicitacoes"), default=Status.pending, index=True)
    changer_by = mapped_column(BigInteger, ForeignKey("usuarios.id"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    __table_args__ = (
        Index(
            "uq_solicitacao_ativa",
            user_id,
            book_id,
            unique = True,
            postgresql_where=is_active.is_(True)
        ),
    )

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

    