from sqlalchemy import ForeignKey, Enum as EnumSQL, UniqueConstraint, Index
from enum import Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timedelta
from .base_model import Base

class Status(str, Enum):
    awaiting_withdrawal = "aguardando retirada"
    awaiting_return = "aguardando devolução"
    returned = "devolvido"
    returned_after_the_deadline = "devolvido fora do prazo"
    not_returned_after_the_deadline = "não devolvido fora do prazo"
    not_returned = "não devolvido"
    canceled = "cancelado"
    lost = "perdido"

    

class LoanModel(Base):
    __tablename__ = "emprestimos"
    

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("livros.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False, index=True)
    status: Mapped[Status] = mapped_column(EnumSQL(Status, name="status_emprestimos"), default=Status.awaiting_withdrawal, index=True)
    unique_book_code_: Mapped[int] = mapped_column(nullable=True, index=True)
    loan_date: Mapped[datetime] = mapped_column(nullable=True)
    return_date: Mapped[datetime] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    __table_args__ = (
        Index(
            "uq_emprestimo_ativo",
            user_id,
            book_id,
            unique = True,
            postgresql_where=is_active.is_(True)
        ),
    )

#Relations
from .user_model import UserModel
from .book_model import BookModel
LoanModel.book = relationship(
    "BookModel",
    back_populates="loans",
    lazy="joined"
)
LoanModel.user = relationship(
    "UserModel",
    back_populates="loans",
    lazy="joined"
)