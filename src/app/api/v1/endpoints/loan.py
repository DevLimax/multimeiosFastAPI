from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from app.models.loan_model import LoanModel, Status as StatusLoan
from app.models.book_model import BookModel
from app.models.user_model import UserModel
from app.schemas.serializers.loan_serializer import BookLoanSchemaBase, BookLoanSchemaUpdate, BookLoanSchemaCreate

from app.utils.exceptions import NotFoundException, NotPermissionsException, UniqueViolationException, InternalServerException
from app.utils.querys_db import search_all_itens_in_db, search_item_in_db
from app.utils.functions import validate_active_loans_limit

from datetime import datetime, timezone, timedelta

from app.core.deps import get_session, get_current_user

router = APIRouter()

#GET All
@router.get(
    "/", 
    response_model=List[BookLoanSchemaBase]
)
async def get_all(
    db: AsyncSession = Depends(get_session)
) -> List[BookLoanSchemaBase]:
    
    async with db as session:
        loans = await search_all_itens_in_db(
            session=session, 
            Model=LoanModel
        )
        return loans
    
    
#GET By ID
@router.get(
    "/{id}", 
    response_model=BookLoanSchemaBase
)
async def get(
    id: int, 
    db: AsyncSession = Depends(get_session)
):
    async with db as session:
        
        loan = await search_item_in_db(
            id=id, 
            session=session, 
            Model=LoanModel
        )
        
        if not loan:
            raise NotFoundException(
                tablename=LoanModel.__tablename__, 
                id=id
            )
        return loan
        
    
#POST Loan
@router.post(
    "/", 
    response_model=BookLoanSchemaBase, 
    status_code=status.HTTP_201_CREATED
)
async def post(
    data: BookLoanSchemaCreate, 
    db: AsyncSession = Depends(get_session), 
    current_user: UserModel = Depends(get_current_user)
) -> Optional[BookLoanSchemaBase]:
    
    async with db as session:
        
        if not current_user.is_admin:
            raise NotPermissionsException()
        
        new_loan = LoanModel(
            book_id = data.book_id,
            user_id = data.user_id,
            status = data.status,
            book_code = data.book_code,
            loan_date = data.date,
            return_date = data.return_date
        )

        if new_loan.status == StatusLoan.awaiting_return and not new_loan.loandate:
            new_loan.loan_date = datetime.now()
        
        if not new_loan.return_date:
            new_loan.return_date = new_loan.date + timedelta(days=20)

            if new_loan.return_date < new_loan.loan_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="A data de devolução não pode ser anterior à data de empréstimo."
                )
        else:
            new_loan.return_date = data.return_date

        user = await search_item_in_db(
            id=data.user_id, 
            session=session, 
            Model=UserModel
        )
        
        if not user:
            raise HTTPException(
                detail="Usuário não existe!",
                status_code=status.HTTP_404_NOT_FOUND
            )
            
        for item in user.loans:
            if item.book_id == data.book_id:

                if item.status in [StatusLoan.returned, StatusLoan.returned_after_the_deadline]:
                    now = datetime.now()
                    fifteen_days = timedelta(days=15)
                    grace_period_for_new_loan = item.return_date + fifteen_days

                    if grace_period_for_new_loan <= now:
                        instance: LoanModel = await search_item_in_db(
                                                        id=item.id, 
                                                        session=session, 
                                                        Model=LoanModel
                                                    )
                        print(instance)
                        await session.delete(instance)
                        await session.commit()
                    else:
                        remaining_days = (grace_period_for_new_loan - now).days
                        raise HTTPException(
                            status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Não é possivel alugar um livro alugado anteriormente ate que a carência de 15 dias expire, faltam {remaining_days} dias"
                        )

                elif item.status in [StatusLoan.awaiting_withdrawal]:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Já existe um emprestimo desse livro para o aluno: ({item.user_id} - {user.first_name + user.last_name}) pendente de retirada"
                    )

                else:
                    print(item.status)
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Já existe um emprestimo desse livro para o aluno: ({item.user_id} - {user.first_name + user.last_name}) pendente de devolução",     
                    )
                
            user = await search_item_in_db(
                id=data.user_id, 
                session=session, 
                Model=UserModel
            )
            validate_active_loans_limit(user)

            book = await search_item_in_db(
                id=data.book_id, 
                session=session, 
                Model=BookModel
            )
            
            if not book:
                raise NotFoundException(
                    tablename=BookModel.__tablename__, 
                    id=data.book_id
                )
                
            if book.quantity <= 0 or not book.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"Essse livro de ID:{book.id} não está disponível para empréstimo."
                )
            
            try:
                session.add(new_loan)
                book.quantity -= 1
                await session.commit()
                await session.refresh(new_loan)
                return new_loan
            except IntegrityError as e:
                print(e)
                if "uniqueviolation" in str(e.orig).lower():
                    raise UniqueViolationException(error=e)
                else:
                    print(e)
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Error: {e.orig}"
                    )
                
            except Exception as e:
                await db.rollback()
                print(e)
                raise InternalServerException()
        
#PUT Loan
@router.put("/{id}", response_model=BookLoanSchemaBase, status_code=status.HTTP_202_ACCEPTED)
async def update(id: int, data: BookLoanSchemaUpdate, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise NotPermissionsException()

    async with db as session:
        instance: Optional[LoanModel] = await search_item_in_db(
                                                    id=id, 
                                                    session=session, 
                                                    Model=LoanModel
                                                )
        if not instance: 
            raise NotFoundException(tablename=LoanModel.__tablename__, id=id)

        if data.return_date and isinstance(data.return_date, str):
            try:
                data.return_date = datetime.strptime(data.return_date, "%d/%m/%Y %H:%M")
            except ValueError:
                raise HTTPException(status_code=400, detail="Formato inválido para a data. Use o formato: DD/MM/AAAA HH:MM")

        for key, value in data.dict(exclude_unset=True).items():
            setattr(instance, key, value)

        if data.status in [StatusLoan.returned, StatusLoan.returned_after_the_deadline]:
            instance.is_active = False

        if data.status == StatusLoan.awaiting_return:

            if not instance.loan_date:
                instance.loan_date = datetime.now()

            if data.return_date:
                if data.return_date < instance.loan_date:
                    raise HTTPException(status_code=400, detail="A data de devolução não pode ser anterior à data de empréstimo.")
                instance.return_date = data.return_date
                
            elif not instance.return_date:
                instance.return_date = instance.loan_date + timedelta(days=20)

        try:
            await session.commit()
            await session.refresh(instance)
            return instance
        except IntegrityError as e:
            if "uniqueviolation" in str(e.orig).lower():
                raise UniqueViolationException(error=e)
            else:
                raise HTTPException(detail=f"Erro de integridade: {e.orig}", status_code=status.HTTP_409_CONFLICT)
        except Exception as e:
            raise InternalServerException()

#DELETE Loan 
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise NotPermissionsException()
        
    async with db as session:
        
        loan = await search_item_in_db(
            id=id, 
            session=session, 
            Model=LoanModel
        
        )
        if not loan:
            raise NotFoundException(
                tablename=LoanModel.__tablename__, 
                id=id
            )

        try:
            await session.delete(loan)
            await session.commit()
            return Response(
                status_code=status.HTTP_204_NO_CONTENT
            )
        
        except Exception as e:
            print(e)
            raise InternalServerException()



    
