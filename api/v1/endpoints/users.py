from typing import List, Optional, Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from models.user_model import UserModel
from schemas.user_schema import UserSchemaBase, UserSchemaWithExtras,UserSchemaCreateForm, UserSchemaUpdateForm

from core.deps import get_session, get_current_user
from core.security import generate_hashed_password
from core.auth import create_access_token, authenticate

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
    user = await authenticate(userInput=form_data.username, password=form_data.password, db=db)

    if not user:
        raise HTTPException(detail="Dados de acesso incorretos!",status_code=status.HTTP_403_FORBIDDEN)
    
    return JSONResponse(content={
        "access_token": create_access_token(sub=user.id), 
        "token_type": "bearer"
    },
    status_code=status.HTTP_200_OK)

#POST User
@router.post("/singup", response_model=UserSchemaBase, status_code=status.HTTP_201_CREATED)
async def create_user(form: UserSchemaCreateForm = Depends(),
                      profileImage: Optional[UploadFile] = File(None),
                      db: AsyncSession = Depends(get_session)
):  
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
            raise HTTPException(detail="Já existe um usuário com esse endereço de email", status_code=status.HTTP_409_CONFLICT)
        
#GET All Users
@router.get("/", response_model=List[UserSchemaBase])
async def get_users(expand: Optional[str] = None, 
                    db: AsyncSession = Depends(get_session)
):
    expand_list = expand.split(",") if expand else []
    async with db as session:
        query = select(UserModel).order_by(UserModel.id)
        result = await session.execute(query)
        users: List[UserModel] = result.scalars().unique().all()
        return users
    
#GET User By ID
@router.get("/{user_id}", response_model=UserSchemaWithExtras, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UserModel).filter(UserModel.id == user_id)
        result = await session.execute(query)
        user = result.scalars().unique().one_or_none()

        if not user:
            raise HTTPException(detail="Usúario não encontrado", 
                                status_code=status.HTTP_404_NOT_FOUND)
        return user
    
#PUT User
@router.put("/{user_id}", response_model=UserSchemaBase, status_code=status.HTTP_202_ACCEPTED)
async def put_user(user_id: int,
                   form: UserSchemaUpdateForm = Depends(),
                   profileImage: Optional[UploadFile] = File(None),
                   db: AsyncSession = Depends(get_session), 
                   current_user: UserModel = Depends(get_current_user)
):
    async with db as session:
        query = select(UserModel).filter(UserModel.id == user_id)
        result = await session.execute(query)
        user_up = result.scalars().unique().one_or_none()

        if not user_up:
            raise HTTPException(detail="Usúario não encontrado", 
                                status_code=status.HTTP_404_NOT_FOUND)
        
        if not current_user.is_admin and user_up.id != current_user.id:
            raise HTTPException(detail="Usuário não tem permissão para alterar outro usuario",status_code=status.HTTP_401_UNAUTHORIZED)
        
        elif current_user.is_admin or user_up.id == current_user.id:
            if form.first_name:
                user_up.first_name = form.first_name.title()
            if form.last_name:
                user_up.last_name = form.last_name.title()
            if form.enrollment:
                user_up.enrollment = form.enrollment
            if form.email:
                user_up.email = form.email
            if form.password:
                user_up.password = generate_hashed_password(form.password)
            if profileImage:
                if profileImage.content_type not in ["image/jpeg", "image/png"]:
                    raise HTTPException(detail="Formato de imagem inválido")
                filename = f"{uuid.uuid4().hex}_{profileImage.filename}"
                filepath = os.path.join("static/images/profiles/", filename)
                with open(filepath, "wb") as buffer:
                    shutil.copyfileobj(profileImage.file, buffer)
                user_up.profile_image = filepath
            if form.is_admin:
                user_up.is_admin = form.is_admin
            if form.is_admin == False:
                user_up.is_admin = False
            if form.is_active:
                user_up.is_active = form.is_active
            if form.is_active == False:
                user_up.is_active = False
        await session.commit()
        await session.refresh(user_up)
        return user_up
    
#DELETE User
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int ,
                      db: AsyncSession = Depends(get_session),
                      current_user: UserModel = Depends(get_current_user)
):
    async with db as session:
        query = select(UserModel).filter(UserModel.id == user_id)
        result = await session.execute(query)
        user = result.scalars().unique().one_or_none()   
    
    if not user:
        raise HTTPException(detail="Usúario não encontrado", 
            status_code=status.HTTP_404_NOT_FOUND)

    if not current_user.is_admin and user.id != current_user.id:
        raise HTTPException(detail="Usuário não tem permissão para excluir outro usuario",
                            status_code=status.HTTP_401_UNAUTHORIZED)
    
    elif current_user.is_admin or user.id == current_user.id:
        async with db as session:
            await session.delete(user)
            await session.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        


