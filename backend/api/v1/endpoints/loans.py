from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from models.bookloan_model import BookLoanModel, Status as StatusLoan
from models.book_model import BookModel
from models.user_model import UserModel

from schemas.bookLoan_schema import BookLoanSchemaBase, BookLoanSchemaUpdate, BookLoanSchemaCreate
from filters.loan_filter import LoansFilter

from utils.exceptionsHttp import not_found, unauthorized, user_book_conflict, exception_not_identified
from utils.search_in_db import search_all_itens_in_db, search_item_in_db
from utils.functions import validate_active_loans_limit

from datetime import datetime, timezone, timedelta

from core.deps import get_session, get_current_user

router = APIRouter()

#GET All
@router.get("/", response_model=List[BookLoanSchemaBase])
async def get_all(db: AsyncSession = Depends(get_session),
                  filters: LoansFilter = Depends()
):
    async with db as session:
        loans = await search_all_itens_in_db(db=session, Model=BookLoanModel, filters=filters)
        return loans
    
#GET By ID
@router.get("/{loan_id}", response_model=BookLoanSchemaBase)
async def get(loan_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        loan = await search_item_in_db(id=loan_id, db=session, Model=BookLoanModel)

        if not loan:
            not_found()

        return loan
    
#POST Loan
@router.post("/", response_model=BookLoanSchemaBase, status_code=status.HTTP_201_CREATED)
async def post(loan: BookLoanSchemaCreate, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        unauthorized()

    new_loan = BookLoanModel(
        book_id = loan.book_id,
        user_id = loan.user_id,
        status = loan.status,
        book_code = loan.book_code,
        loan_date = loan.loan_date,
        return_date = loan.return_date
    )

    if new_loan.status == StatusLoan.awaiting_return and not new_loan.loan_date:
        new_loan.loan_date = datetime.now()
        if not new_loan.return_date:
            new_loan.return_date = new_loan.loan_date + timedelta(days=20)

        if new_loan.return_date < new_loan.loan_date:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A data de devolução não pode ser anterior à data de empréstimo.")
        else:
            new_loan.return_date = loan.return_date

    user = await search_item_in_db(id=loan.user_id, db=db, Model=UserModel)
    if not user:
        raise HTTPException(detail="Usuário não existe!",status_code=status.HTTP_404_NOT_FOUND)
        
    for loan_item in user.loans:
        if loan_item.book_id == loan.book_id:

            if loan_item.status in [StatusLoan.returned, StatusLoan.returned_after_the_deadline]:
                now = datetime.now()
                fifteen_days = timedelta(days=15)
                grace_period_for_new_loan = loan_item.return_date + fifteen_days

                if grace_period_for_new_loan <= now:
                    loan_db: BookLoanModel = await search_item_in_db(id=loan_item.id, db=db, Model=BookLoanModel)
                    print(loan_db)
                    await db.delete(loan_db)
                    await db.commit()
                else:
                    remaining_days = (grace_period_for_new_loan - now).days
                    raise HTTPException(detail=f"Não é possivel alugar um livro alugado anteriormente ate que a carência de 15 dias expire, faltam {remaining_days} dias", 
                                        status_code=status.HTTP_406_NOT_ACCEPTABLE)
                
            elif loan_item.status == StatusLoan.canceled:
                db.delete(loan_item)
                db.commit()

            elif loan_item.status in [StatusLoan.awaiting_withdrawal]:
                raise HTTPException(detail=f"Já existe um emprestimo desse livro para o aluno: ({loan_item.user_id} - {user.first_name + user.last_name}) pendente de retirada", status_code=status.HTTP_400_BAD_REQUEST)

            else:
                print(loan_item.status)
                raise HTTPException(detail=f"Já existe um emprestimo desse livro para o aluno: ({loan_item.user_id} - {user.first_name + user.last_name}) pendente de devolução", status_code=status.HTTP_400_BAD_REQUEST)

    async with db as session:
        user = await search_item_in_db(id=loan.user_id, db=session, Model=UserModel)
        validate_active_loans_limit(user=user)

        book = await search_item_in_db(id=loan.book_id, db=session, Model=BookModel)
        if not book:
            raise HTTPException(detail="Livro nao existe!", status_code=status.HTTP_404_NOT_FOUND)
            
        if book.quantity <= 0 or not book.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Essse livro de ID:{book.id} não está disponível para empréstimo.")
        
        try:
            session.add(new_loan)
            book.quantity -= 1
            await session.commit()
            await session.refresh(new_loan)
            return new_loan
        except IntegrityError as e:
            user_book_conflict(tablename=BookLoanModel.__tablename__)
        except Exception as e:
            exception_not_identified(error=e)
        
#PUT Loan
@router.put("/{loan_id}", response_model=BookLoanSchemaBase, status_code=status.HTTP_202_ACCEPTED)
async def update(loan_id: int, loan: BookLoanSchemaUpdate, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        unauthorized()

    async with db as session:
        loan_db = await search_item_in_db(id=loan_id, db=session, Model=BookLoanModel)
        if not loan_db:
            not_found()  

        if loan.return_date and isinstance(loan.return_date, str):
            try:
                loan.return_date = datetime.strptime(loan.return_date, "%d/%m/%Y %H:%M")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato inválido para a data. Use o formato: DD/MM/AAAA HH:MM")

        for key, value in loan.dict(exclude_unset=True).items():
            setattr(loan_db, key, value)

        if loan.status in [StatusLoan.returned, StatusLoan.returned_after_the_deadline]:
            loan_db.is_active = False

        if loan.status == StatusLoan.awaiting_return:

            if not loan_db.loan_date:
                loan_db.loan_date = datetime.now()

            if loan.return_date:
                if loan.return_date < loan_db.loan_date:
                    raise HTTPException(status_code=400, detail="A data de devolução não pode ser anterior à data de empréstimo.")
                loan_db.return_date = loan.return_date

            elif not loan_db.return_date:
                loan_db.return_date = loan_db.loan_date + timedelta(days=20)

        await session.commit()
        await session.refresh(loan_db)
        return loan_db

#DELETE Loan 
@router.delete("/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(loan_id: int, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        unauthorized()

    async with db as session:
        loan = await search_item_in_db(id=loan_id, db=session, Model=BookLoanModel)
        if not loan:
            not_found()

        try:
            await db.delete(loan)
            await db.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            exception_not_identified(error=e)



    

    
