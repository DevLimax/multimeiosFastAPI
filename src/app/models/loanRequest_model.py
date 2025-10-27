from sqlalchemy import ForeignKey, UniqueConstraint, Enum as EnumSQL, Index, BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from .base_model import Base
from enum import Enum

class Status(str, Enum):
    pending = "pendente"
    approved = "aprovado"
    denied = "negado"
    
class ReasonChoices(str, Enum):
    lack_stock = "falta de estoque"
    user_limit = "limite de empréstimos"
    user_fines = "multas pendentes"
    other = "outro"
    
class LoanRequestModel(Base):
    __tablename__ = "solicitacoes_emprestimos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, index=True)
    book_id = mapped_column(BigInteger, ForeignKey("livros.id"), nullable=False, index=True)
    user_id = mapped_column(BigInteger, ForeignKey("usuarios.id"), nullable=False, index=True)
    status = mapped_column(EnumSQL(Status, name="status_solicitacoes"), default=Status.pending, index=True)
    reason: Mapped[ReasonChoices] = mapped_column(EnumSQL(ReasonChoices, name="motivos_solicitacoes"), nullable=True)
    other_reason: Mapped[str] = mapped_column(String(60), nullable=True)
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
LoanRequestModel.loan = relationship(
    "LoanModel",
    back_populates="request",
    lazy="joined"
)