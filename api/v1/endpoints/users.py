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
    Retorna o usuário criado ou um erro 409-Conflict se já existir um usuário com o mesmo email ou matrícula.

    Campos obrigatórios:
    - username: Nome de usuário único.
    - email: Endereço de email único.
    - password: Senha do usuário.

    Campos que devem ser únicos:
    - enrollment: Matrícula do usuário (opcional, mas se fornecida, deve ser única).
    - email: Endereço de email (obrigatório, deve ser único).
    - username: Nome de usuário (obrigatório, deve ser único).

    A grande maioria dos campos são opcionais e preenchem com default ja fornecido no Models, mas se fornecidos, devem ser válidos.
    """

    if profileImage:
        if profileImage.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(detail="Formato de imagem inválido")
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
        except IntegrityError:
            raise HTTPException(detail="Já existe um usuário com esse endereço de email ou matricula", status_code=status.HTTP_409_CONFLICT)
        
#GET All Users
@router.get("/", response_model=List[UserSchemaBase])
async def get_users( db: AsyncSession = Depends(get_session)):
    async with db as session:
        users = await search_all_itens_in_db(Model=UserModel, db=db)
        return users
    
#GET User By ID
@router.get("/{user_id}", response_model=UserSchemaWithExtras, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, 
                   db: AsyncSession = Depends(get_session)):
    async with db as session:
        user = await search_item_in_db(id=user_id, db=session, Model=UserModel)
        if not user:
            not_found()
        return user
    
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
                raise HTTPException(detail="Formato de imagem inválido")
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
            
    
