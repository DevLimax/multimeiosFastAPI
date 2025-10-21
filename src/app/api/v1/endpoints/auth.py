from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import UserModel
from app.schemas.serializers.user_serializer import UserSchemaWithExtras

from app.core.deps import get_session, get_current_user
from app.core.auth import create_access_token, authenticate

router = APIRouter()

@router.get(
    '/logged', 
    response_model=UserSchemaWithExtras, 
    status_code=status.HTTP_200_OK
)
def get_logged(
    user: UserModel = Depends(get_current_user)
):
    return user

#POST Login
@router.post(
    "/login"
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: AsyncSession = Depends(get_session)
):
    """
        Endpoint para autenticação de usuário.

        Recebi um formulário com username que recebe username ou email junto com password.
        Retorna um token de acesso se as credenciais estiverem corretas.
        Caso contrário, retorna um erro 401-Unauthorized.
    """
    user = await authenticate(userInput=form_data.username, password=form_data.password, db=db)

    if not user:
        raise HTTPException(detail="Dados de acesso incorretos!",status_code=status.HTTP_401_UNAUTHORIZED)
    
    return JSONResponse(content={
        "access_token": create_access_token(sub=user.id), 
        "token_type": "bearer"
    },
    status_code=status.HTTP_200_OK)