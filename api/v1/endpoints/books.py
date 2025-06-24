from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from models.user_model import UserModel
from models.book_model import BookModel
from schemas.book_schema import BookSchemaBase, BookSchemaReviews, BookSchemaUpdateForm, BookSchemaForm

from utils.search_in_db import *
from utils.exceptionsHttp import not_found, exception_not_identified, unauthorized

from core.deps import get_session, get_current_user

import os
import shutil
import uuid

router = APIRouter()

#GET All Books
@router.get("/", response_model=List[BookSchemaBase], status_code=status.HTTP_200_OK)
async def get_books(db: AsyncSession = Depends(get_session)):
    books = await search_all_itens_in_db(db=db, Model=BookModel)
    return books
    
#GET Book by ID
@router.get("/{book_id}", response_model=BookSchemaBase, status_code=status.HTTP_200_OK)
async def get_book(book_id: int, db: AsyncSession = Depends(get_session)):
    book = await search_item_in_db(id=book_id, db=db, Model=BookModel)
    if not book:
        not_found()

    return book
    
#GET Book by ID with Reviews
@router.get("/{book_id}/reviews", response_model=BookSchemaReviews, status_code=status.HTTP_200_OK)
async def get_book_reviews(book_id:int, db: AsyncSession = Depends(get_session)):
    book = await search_item_in_db(id=book_id, db=db, Model=BookModel)
    if not book:
        not_found()

    return book
    
#POST Book
@router.post("/", response_model=BookSchemaBase, status_code=status.HTTP_201_CREATED)
async def create_book(form: BookSchemaForm = Depends(), 
                      fileCover: Optional[UploadFile] = File(None),
                      db: AsyncSession = Depends(get_session), 
                      current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario não autorizado")

    if fileCover:
        if fileCover.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(detail="Formato de imagem inválido")
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
        added_by=current_user.id
    )

    try:
        db.add(new_book)
        await db.commit()
        await db.refresh(new_book)
        return new_book
    except IntegrityError:
        raise HTTPException(detail="Já existe uma instancia na tabela (Livros) com o mesmo Titulo e Autor")
    except Exception as e:
        exception_not_identified(error=e)

#PUT Book
@router.put("/{book_id}", response_model=BookSchemaBase, status_code=status.HTTP_200_OK)
async def update_book(book_id: int,
                      book: BookSchemaUpdateForm = Depends(),
                      fileCover: Optional[UploadFile] = File(None),
                      db: AsyncSession = Depends(get_session),
                      current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        unauthorized()
    
    book_db = await search_item_in_db(id=book_id, db=db, Model=BookModel)

    if not book_db:
        not_found()
    
    for key, value in book.__dict__.items():
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

    await db.commit()
    await db.refresh(book_db)
    return book_db
    
#DELETE Book
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_book(book_id: int, 
                   db: AsyncSession = Depends(get_session),
                   current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        unauthorized()

    book = await search_item_in_db(id=book_id, db=db, Model=BookModel)

    if not book:
        not_found()
    
    await db.delete(book)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


