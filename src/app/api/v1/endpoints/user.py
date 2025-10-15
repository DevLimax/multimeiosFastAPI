from typing import List, Optional, Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from app.models.user_model import UserModel
from app.models.loan_model import Status
from app.schemas.serializers.user_serializers import UserSchemaBase, UserSchemaWithExtras, UserSchemaCreateForm, UserSchemaUpdateForm

from app.core.deps import get_session, get_current_user
from app.core.security import generate_hashed_password

from app.utils.querys_db import search_item_in_db, search_all_itens_in_db
from app.utils.exceptions import UniqueViolationException, NotFoundException

from datetime import datetime
import os
import shutil
import uuid

router = APIRouter()

#POST User
@router.post(
    "/", 
    response_model=UserSchemaBase, 
    status_code=status.HTTP_201_CREATED
)
async def create_user(
    form: UserSchemaCreateForm = Depends(),
    profileImage: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_session)
):  

    if profileImage:
        try:
            if profileImage.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(detail="Formato de imagem inválido", status_code=status.HTTP_400_BAD_REQUEST)
            filename = f"{uuid.uuid4().hex}_{profileImage.filename}"
            filepath = os.path.join("src/app/static/images/profiles/", filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(profileImage.file, buffer)
        except Exception as e:
            print(e)
            raise HTTPException(detail="Erro ao salvar imagem", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    else:
        filepath = "src/app/static/images/profiles/defaultProfile.png"

    
    new_user = UserModel(
        first_name = form.first_name,
        last_name = form.last_name,
        enrollment = form.enrollment,
        email = form.email,
        password = generate_hashed_password(form.password),
        is_admin = form.is_admin,
        profile_image = filepath
    )
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    
    except IntegrityError as e:
        await db.rollback()
        if "uniqueviolation" in str(e.orig).lower():
            raise UniqueViolationException(error=e)
        else:
            raise HTTPException(detail=f"Erro de integridade: {e.orig}", status_code=status.HTTP_409_CONFLICT)
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(detail="Erro interno do servidor", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#GET All Users
@router.get("/", response_model=List[UserSchemaBase])
async def get_users( db: AsyncSession = Depends(get_session)):
    """
    Retorna todos os usuários cadastrados na base de dados. ou -> []
    """
    async with db as session:
        users = await search_all_itens_in_db(Model=UserModel, session=db)
        try:
            return users
        except Exception as e:
            raise HTTPException(detail="Erro interno do servidor", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#GET User By ID
@router.get("/{id}", response_model=UserSchemaWithExtras, status_code=status.HTTP_200_OK)
async def get_user(id: int, 
                   db: AsyncSession = Depends(get_session)):
        
    async with db as session:
        user = await search_item_in_db(id=id, session=session, Model=UserModel)
        if not user:
            raise NotFoundException(id=id)
                      
        return user
    
#PUT User
@router.put("/{id}", response_model=UserSchemaBase, status_code=status.HTTP_202_ACCEPTED)
async def put_user(id: int,
                   user: UserSchemaUpdateForm = Depends(),
                   profileImage: Optional[UploadFile] = File(None),
                   db: AsyncSession = Depends(get_session), 
                   current_user: UserModel = Depends(get_current_user)
):
        user_db = await search_item_in_db(id=id, session=db, Model=UserModel)

        if not user_db:
            raise NotFoundException(id=id)
        
        if not current_user.is_admin and user_db.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        
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

        try:
            await db.commit()
            await db.refresh(user_db)
            return user_db
        except IntegrityError as e:
            await db.rollback()
            e_str = str(e.orig).lower()
            if "unique constraint" in str(e.orig).lower():
                if "email" in e_str:
                    raise HTTPException(detail=f"Já existe uma instancia com (email = {user.email})", status_code=status.HTTP_409_CONFLICT)
                else:
                    raise HTTPException(detail=f"Já existe uma instancia com (enrollment = {user.enrollment})", status_code=status.HTTP_409_CONFLICT)
            else:
                raise HTTPException(detail=f"Erro de integridade {e.orig}", status_code=status.HTTP_409_CONFLICT)
    
        except Exception as e:
            await db.rollback()
            print(e)
            raise HTTPException(detail="Erro interno do servidor", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
#DELETE User
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int ,
                      db: AsyncSession = Depends(get_session),
                      current_user: UserModel = Depends(get_current_user)
):
    async with db as session:
        user = await search_item_in_db(id=id, session=session, Model=UserModel)
        if not user:
            raise NotFoundException(id=id)

        if not current_user.is_admin and user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        
        elif current_user.is_admin or user.id == current_user.id:
            try:
                await session.delete(user)
                await session.commit()
                return Response(status_code=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                await session.rollback()
                raise HTTPException(detail="Erro interno do servidor", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    