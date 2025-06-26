from typing import List, Optional, Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from models.user_model import UserModel
from models.bookloan_model import Status
from schemas.user_schema import UserSchemaBase, UserSchemaWithExtras,UserSchemaCreateForm, UserSchemaUpdateForm

from core.deps import get_session, get_current_user
from core.security import generate_hashed_password
from core.auth import create_access_token, authenticate

from utils.exceptionsHttp import not_found, unauthorized, exception_not_identified
from utils.search_in_db import search_all_itens_in_db, search_item_in_db
from utils.functions import user_expands

from datetime import datetime
import os
import shutil
import uuid

router = APIRouter()

#GET Logged User
@router.get('/logged', response_model=UserSchemaWithExtras, status_code=status.HTTP_200_OK)
def get_logged(user: UserModel = Depends(get_current_user)):
    return user

#POST Login
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
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

#POST User
@router.post("/signup", response_model=UserSchemaBase, status_code=status.HTTP_201_CREATED)
async def create_user(form: UserSchemaCreateForm = Depends(),
                      profileImage: Optional[UploadFile] = File(None),
                      db: AsyncSession = Depends(get_session)
):  
    """
    Criação de usuário.

    Recebe um formulário com os dados do usuário e uma imagem de perfil opcional.
    Se a imagem for fornecida, deve ser do tipo JPEG ou PNG.
    Se não for fornecida, será usada uma imagem padrão.

    Campos:
    - username: Nome de usuário (obrigatório, deve ser único)..
    - email: Endereço de email único.(obrigatório, deve ser único).
    - password: Senha do usuário. (obrigatório).
    - first_name: Primeiro nome do usuário (opcional).
    - last_name: Sobrenome do usuário (opcional).
    - enrollment: Matrícula do usuário (opcional, deve ser único).
    - is_admin: Permissão de admin do usuário (opcional - preenchido automaticamente como False).
    - profile_image: Imagem de perfil do usuário (opcional - retorna uma imagem default caso seja null).

    A grande maioria dos campos são opcionais e preenchem com default ja fornecido no Models, mas se fornecidos, devem ser válidos.
    
    Exceptions:
    - HTTPException 409-Conflict: Se o username, email ou matrícula do usuário já existir na base de dados.
    - HTTPException 400-Bad Request: Se a imagem de perfil for fornecida e não for do tipo JPEG ou PNG.
    - HTTP 422 Unprocessable Entity: Se o formulário for inválido.
    - HTTP 500 Internal Server Error: Se houver algum erro interno no servidor.
    """

    if profileImage:
        if profileImage.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(detail="Formato de imagem inválido", status_code=status.HTTP_400_BAD_REQUEST)
        filename = f"{uuid.uuid4().hex}_{profileImage.filename}"
        filepath = os.path.join("static/images/profiles/", filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(profileImage.file, buffer)
    else:
        filepath = "static/images/profiles/defaultProfile.png"

    async with db as session:
        new_user = UserModel(
            username = form.username,
            first_name = form.first_name,
            last_name = form.last_name,
            enrollment = form.enrollment,
            email = form.email,
            password = generate_hashed_password(form.password),
            is_admin = form.is_admin,
            profile_image = filepath
        )
        try:
            session.add(new_user)
            await session.commit()
            return new_user
        except IntegrityError as e:
            error_Str = str(e).lower()
            print(error_Str)
            
            if "(username)" in error_Str:
                campo = "Nome de usuário"
                
            elif "(email)" in error_Str:
                campo = "Endereço de email"
                
            elif "(enrollment)" in error_Str:
                campo = "Matrícula"
                
            session.rollback()
            raise HTTPException(detail=f"{campo} já cadastrado", status_code=status.HTTP_409_CONFLICT)
        
        except Exception as e:
            session.rollback()
            raise exception_not_identified(e)
        
#GET All Users
@router.get("/", response_model=List[UserSchemaBase])
async def get_users( db: AsyncSession = Depends(get_session)):
    """
    Retorna todos os usuários cadastrados na base de dados. ou -> []
    """
    async with db as session:
        users = await search_all_itens_in_db(Model=UserModel, db=db)
        try:
            return users
        except Exception as e:
            raise exception_not_identified(e)
    
#GET User By ID
@router.get("/{user_id}", response_model=UserSchemaWithExtras, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, 
                   expand: Optional[str] = None,
                   db: AsyncSession = Depends(get_session)):
    if expand:
        expand = expand.split(",")
        
    async with db as session:
        user = await search_item_in_db(id=user_id, db=session, Model=UserModel)
        if not user:
            not_found()
            
        
        user_dict = user_expands(user=user, expand=expand)            
        return user_dict
    
#PUT User
@router.put("/{user_id}", response_model=UserSchemaBase, status_code=status.HTTP_202_ACCEPTED)
async def put_user(user_id: int,
                   user: UserSchemaUpdateForm = Depends(),
                   profileImage: Optional[UploadFile] = File(None),
                   db: AsyncSession = Depends(get_session), 
                   current_user: UserModel = Depends(get_current_user)
):
    async with db as session:
        user_db = await search_item_in_db(id=user_id, db=session, Model=UserModel)

        if not user_db:
            not_found()
        
        if not current_user.is_admin and user_db.id != current_user.id:
            unauthorized()
        
        elif current_user.is_admin or user_db.id == current_user.id:
            for key, value in user.__dict__.items():
                if value is not None:
                    setattr(user_db, key, value)
        
        if profileImage:
            if profileImage.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(detail="Formato de imagem inválido", status_code=status.HTTP_400_BAD_REQUEST)
            filename = f"{uuid.uuid4().hex}_{profileImage.filename}"
            filepath = os.path.join("static/images/profiles/", filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(profileImage.file, buffer)
            user_db.profile_image = filepath
    
        await session.commit()
        await session.refresh(user_db)
        return user_db
    
#DELETE User
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int ,
                      db: AsyncSession = Depends(get_session),
                      current_user: UserModel = Depends(get_current_user)
):
    async with db as session:
        user = await search_item_in_db(id=user_id, db=session, Model=UserModel)
        if not user:
            not_found()

        if not current_user.is_admin and user.id != current_user.id:
            unauthorized()
        
        elif current_user.is_admin or user.id == current_user.id:
            try:
                await session.delete(user)
                await session.commit()
                return Response(status_code=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                exception_not_identified(error=e)
            
    
