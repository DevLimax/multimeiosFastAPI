from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from models.bookloan_model import BookLoanModel
from models.book_model import BookModel
from models.user_model import UserModel
from schemas.bookLoan_schema import BookLoanSchemaBase, BookLoanSchemaUpdate, BookLoanSchemaCreate

from utils.exceptionsHttp import not_found, unauthorized, user_book_conflict, exception_not_identified
from utils.search_in_db import search_all_itens_in_db, search_item_in_db

from datetime import datetime

from core.deps import get_session, get_current_user

router = APIRouter()

#GET All
@router.get("/", response_model=List[BookLoanSchemaBase])
async def get_all(db: AsyncSession = Depends(get_session)):
    loans = await search_all_itens_in_db(db=db, Model=BookLoanModel)
    return loans
    
#GET By ID
@router.get("/{loan_id}", response_model=BookLoanSchemaBase)
async def get(loan_id: int, db: AsyncSession = Depends(get_session)):
    loan = await search_item_in_db(id=loan_id, db=db, Model=BookLoanModel)

    if not loan:
        not_found()

    return loan
    
#POST Loan
@router.post("/", response_model=BookLoanSchemaBase, status_code=status.HTTP_201_CREATED)
async def post(loan: BookLoanSchemaCreate, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(detail="Usuário sem autorização para realizar ação", status_code=status.HTTP_401_UNAUTHORIZED)

    new_loan = BookLoanModel(
        book_id = loan.book_id,
        user_id = loan.user_id,
        status = loan.status,
        loan_date = loan.loan_date,
        return_date = loan.return_date
    )

    async with db as session:
        try:
            session.add(new_loan)
            await session.commit()
            await session.refresh(new_loan)
            return new_loan
        except IntegrityError:
            user_book_conflict(tablename=BookLoanModel.__tablename__)
        except Exception as e:
            exception_not_identified(error=e)
        
#PUT Loan
@router.put("/{loan_id}", response_model=BookLoanSchemaUpdate, status_code=status.HTTP_202_ACCEPTED)
async def update(loan_id: int, loan: BookLoanSchemaUpdate, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        unauthorized()

    loan_db = await search_item_in_db(id=loan_id, db=db, Model=BookLoanModel)
    if not loan_db:
        not_found()

    for key, value in loan.dict(exclude_unset=True).items():
        setattr(loan_db, key, value)
    loan_db.updated_at = datetime.now()

    await db.commit()
    await db.refresh(loan_db)
    return loan_db

#DELETE Loan 
@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(loan_id: int, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        unauthorized()

    loan = search_item_in_db(id=loan_id, db=db, Model=BookLoanModel)
    if not loan:
        not_found()

    try:
        await db.delete(loan)
        await db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        exception_not_identified(error=e)



    

    
