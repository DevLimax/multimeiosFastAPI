from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, DateTime
from sqlalchemy.orm import relationship
from core.configs import settings
from datetime import datetime, timedelta

class Base(settings.DBBASEMODEL):
    __abstract__ = True
    
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)
    is_active = Column(Boolean, nullable=False, default=True)
    
