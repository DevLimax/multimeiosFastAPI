from sqlalchemy import Boolean, func    
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.configs import settings
from datetime import datetime

class Base(settings.DBBASEMODEL):
    __abstract__ = True
    
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=datetime.utcnow, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(nullable=True, default=datetime.utcnow, onupdate=func.now())
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    