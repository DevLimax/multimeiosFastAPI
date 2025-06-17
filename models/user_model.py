from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from core.configs import settings

class UserModel(settings.DBBASEMODEL):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    enrollment = Column(Integer, nullable=True)
    email = Column(String(256), index=True, nullable=False, unique=True)
    password = Column(String(256), index=True, nullable=False)
    is_admin = Column(Boolean, default=False)
    profile_image = Column(String(255), default="static/images/defaultProfile.png")
    loans = relationship(
        "BookLoanModel",
        cascade="all, delete-orphan",
        back_populates="user",
        lazy="joined"
    )