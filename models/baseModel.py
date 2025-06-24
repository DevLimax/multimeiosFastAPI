from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, DateTime, func    
from sqlalchemy.orm import relationship
from core.configs import settings
from datetime import datetime, timedelta

class Base(settings.DBBASEMODEL):
    __abstract__ = True
    
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=True, default=datetime.utcnow, onupdate=func.now())
    is_active = Column(Boolean, nullable=False, default=True)
    
