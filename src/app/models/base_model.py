from sqlalchemy import Boolean, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.configs import settings
from datetime import datetime, timezone

class Base(settings.DBBASEMODEL):
    __abstract__ = True
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), # <-- CORREÇÃO: Indica que é com fuso horário
        nullable=False,
        default=lambda: datetime.now(timezone.utc), # Garantindo que o valor Python seja aware (UTC)
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), # <-- CORREÇÃO: Indica que é com fuso horário
        nullable=True,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc) # onupdate DEVE ser um callable para rodar na atualização do objeto
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    