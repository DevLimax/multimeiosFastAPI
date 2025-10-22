from pytz import timezone
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from pydantic import EmailStr
from sqlalchemy.future import select
from sqlalchemy import or_, cast, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt

from app.models import UserModel
from app.core.configs import settings
from app.core.security import verify_password

oauth2_schema = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def authenticate(userInput: str, password: str, db: AsyncSession) -> Optional[UserModel]:
    async with db as session:
        try:
            enrollment_value = int(userInput)
            query = select(UserModel).filter(or_(
                UserModel.email == userInput,
                UserModel.enrollment == cast(enrollment_value, Integer)
            ))
        except ValueError:
            query = select(UserModel).filter(or_(
                UserModel.email == userInput
            ))
        result = await session.execute(query)
        user: UserModel =  result.scalars().unique().one_or_none()

        if not user:
            return None
        
        if not verify_password(password=password, hashed_password=user.password):
            return None
        
        user.last_login = datetime.now()
        await session.commit()
        await session.refresh(user)
        
        return user
    
def create_token(type_token: str, timelife: timedelta, sub: str) -> str:
    payload = {}
    sp = timezone("America/Sao_Paulo")
    expired = datetime.now(tz=sp) + timelife

    payload["type"] = type_token
    payload["exp"] = expired
    payload["iat"] = datetime.now(tz=sp)
    payload["sub"] = str(sub)

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM)

def create_access_token(sub: str) -> str:
    return create_token(
        type_token="access_token",
        timelife=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRED),
        sub=sub
    )