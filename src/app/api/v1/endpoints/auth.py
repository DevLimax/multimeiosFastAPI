from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import UserModel
from app.schemas.serializers.user_serializer import UserSchemaWithExtras, VerifyCodeSchema
from app.Emails.send_email import send_email_verification_code

from app.core.deps import get_session, get_current_user
from app.core.auth import create_access_token, authenticate
from app.utils.querys_db import search_item_in_db
from app.utils.exceptions import NotVerifiedException

from datetime import datetime, timezone

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
    
#POST verify_code
@router.post("/verify_code", status_code=status.HTTP_200_OK)
async def verify_code(data: VerifyCodeSchema, 
                      db: AsyncSession = Depends(get_session),
                      user: UserModel = Depends(get_current_user)
) -> JSONResponse:
    
    if user.is_active:
        return JSONResponse(content={"message": "Usuário ja verificado!"}, status_code=status.HTTP_200_OK)
    
    if not user.verification_code or not user.verification_code_expiration:
        return JSONResponse(content={"message": "Solicitar um novo código"}, status_code=status.HTTP_400_BAD_REQUEST)
    
    async with db as session:
        user_db: UserModel = await search_item_in_db(id=user.id, session=session, Model=UserModel)
        
        if user_db.verification_code == data.code:
            if user_db.verification_code_expiration < datetime.now(timezone.utc):
                return JSONResponse(content={"message": "Código de verificação expirado"}, status_code=status.HTTP_408_REQUEST_TIMEOUT)
                
            user_db.is_active = True
            user_db.verification_code = None
            user_db.verification_code_expiration = None
            await db.commit()
            await db.refresh(user_db)
            return JSONResponse(content={"message": "Usuário verificado com sucesso!"}, status_code=status.HTTP_202_ACCEPTED)
        
        return JSONResponse(content={"message": "Código de verificação inválido"}, status_code=status.HTTP_400_BAD_REQUEST)

#POST resend_code
@router.post("/resend_code", status_code=status.HTTP_200_OK)
async def resend_code(user: UserModel = Depends(get_current_user),
                      db: AsyncSession = Depends(get_session)
) -> JSONResponse:
    if user.is_active:
        return JSONResponse(content={"message": "Usuário ja verificado!"}, status_code=status.HTTP_200_OK)
    
    async with db as session:
        user_db = await search_item_in_db(id=user.id, session=session, Model=UserModel)
        
        try:
            await user_db.generate_verification_code()
            await db.commit()
            await db.refresh(user_db)
            send_email_verification_code(receiver_email=user.email, 
                                         code=user_db.verification_code, 
                                         username=user.first_name)
            
            return JSONResponse(content={"message": "Código de verificação reenviado com sucesso!"}, status_code=status.HTTP_201_CREATED)
        
        except Exception as e:
            await session.rollback()
            return JSONResponse(content={"message": f"Erro ao reenviar código de verificação: {e}"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)