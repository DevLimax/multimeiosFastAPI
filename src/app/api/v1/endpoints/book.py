from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError

from app.models.user_model import UserModel
from app.models.book_model import BookModel
from app.schemas.serializers.book_serializer import BookSchemaBase, BookSchemaReviews, BookSchemaUpdateForm, BookSchemaForm

from app.utils.querys_db import search_all_itens_in_db, search_item_in_db
from app.utils.exceptions import InternalServerException, NotFoundException, NotPermissionsException

from app.core.deps import get_session, get_current_user

import os
import shutil
import uuid

router = APIRouter()

#GET All Books
@router.get("/", response_model=List[BookSchemaBase], status_code=status.HTTP_200_OK)
async def get_books(db: AsyncSession = Depends(get_session)):
    async with db as session:
        books = await search_all_itens_in_db(session=session, Model=BookModel)
        return books
        
#GET Book by ID
@router.get(
    "/{id}", 
    response_model=BookSchemaBase, 
    status_code=status.HTTP_200_OK
)
async def get_book(
    id: int, 
    db: AsyncSession = Depends(get_session)
):

    async with db as session:
        book = await search_item_in_db(
            id=id, 
            session=session, 
            Model=BookModel
        )
        if not book:
            raise NotFoundException(id=id)

        return book
    
#GET Book by ID with Reviews
@router.get(
    "/{id}/reviews", 
    response_model=BookSchemaReviews, 
    status_code=status.HTTP_200_OK
)
async def get_book_reviews(
    id:int, db: AsyncSession = Depends(get_session)
):
    async with db as session:
        book = await search_item_in_db(id=id, session=session, Model=BookModel)
        if not book:
            raise NotFoundException(id=id)

        return book
    
#POST Book
@router.post(
    "/", 
    response_model=BookSchemaBase, 
    status_code=status.HTTP_201_CREATED
)
async def create_book(
    form: BookSchemaForm = Depends(), 
    fileCover: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_session), 
    current_user: UserModel = Depends(get_current_user)
):  
    async with db as session:

        if not current_user.is_admin:
            raise NotPermissionsException()

        if fileCover:
            if fileCover.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(detail="Formato de imagem inválido", status_code=status.HTTP_400_BAD_REQUEST)
            filename = f"{uuid.uuid4().hex}_{fileCover.filename}"
            filepath = os.path.join("static/images/covers/", filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(fileCover.file, buffer)
        else:
            filepath = "static/images/covers/bookDefault.png"

        new_book = BookModel(
            title=form.title,
            author=form.author,
            synopsis=form.synopsis,
            genre_id=form.genre,
            genre_two_id=form.genre_two,
            quantity=form.quantity,
            cover=filepath,
            added_by_id=current_user.id
        )

        try:
            db.add(new_book)
            await db.commit()
            await db.refresh(new_book)
            return new_book
        
        except IntegrityError as e:
            await db.rollback()
            if "uniqueviolation" in str(e.orig).lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Já existe uma instancia com mesmo titulo: {new_book.title} e autor: {new_book.author}"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Error de integridade: {e.orig}"
                )

        except Exception as e:
            await db.rollback()
            raise InternalServerException()

#PUT Book
@router.put("/{book_id}", response_model=BookSchemaBase, status_code=status.HTTP_200_OK)
async def update_book(book_id: int,
                      data: BookSchemaUpdateForm = Depends(),
                      fileCover: Optional[UploadFile] = File(None),
                      db: AsyncSession = Depends(get_session),
                      current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise NotPermissionsException()
        
    async with db as session:
        book_db: BookModel = await search_item_in_db(id=book_id, session=session, Model=BookModel)

        if not book_db:
            raise NotFoundException(id)
        
        new_tiltle = data.title if data.title else book_db.title
        new_author = data.author if data.author else book_db.author
        
        if new_tiltle == book_db.title or new_author == book_db.author:
            collision_check_stmt = select(BookModel).where(
                and_(
                    BookModel.title == new_tiltle,
                    BookModel.author == new_author,
                    BookModel.id != book_db.id
                )
            )
            collision_result = await session.execute(collision_check_stmt)
            if collision_result.first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Já existe uma instancia com mesmo titulo: {new_tiltle} e autor: {new_author}"
                )
        
        for key, value in data.__dict__.items():
            if value is not None:
                setattr(book_db, key, value)
        
        if fileCover:
            if fileCover.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(detail="Formato de imagem inválido")
            filename = f"{uuid.uuid4().hex}_{fileCover.filename}"
            filepath = os.path.join("static/images/covers/", filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(fileCover.file, buffer)
            book_db.cover = filepath
        
        await session.commit()
        await session.refresh(book_db)
        return book_db
    
#DELETE Book
@router.delete(
    "/{id}", 
    status_code=status.HTTP_204_NO_CONTENT
)
async def del_book(
    id: int, 
    db: AsyncSession = Depends(get_session),
    current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise NotPermissionsException

    async with db as session:
        book = await search_item_in_db(id=id, session=session, Model=BookModel)

        if not book:
            raise NotFoundException(id)
        await session.delete(book)
        await session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)