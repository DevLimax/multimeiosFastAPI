from app.models.loanRequest_model import LoanRequestModel, Status
from app.core.db import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
import asyncio

async def create(
    user_id: int,
    booK_id: int
):
    
    async with Session() as session:
        request = LoanRequestModel(
            user_id = user_id,
            book_id = booK_id,
            status = Status.approved
        )
        try:
            session.add(request)
            await session.commit()
            await session.refresh(request)
            return print(request.__dict__)
        except IntegrityError as e:
            await session.rollback()
            if "uniqueviolation" in str(e.orig).lower():
                return print(f"Usuário ja possui uma solicitação ativa para o livro: {booK_id}")
            
            if "foreigkeyviolation" in str(e.orig).lower():
                return print(f"O livro: {booK_id} nao existe")
            return print(e.orig)
        
        except Exception as e:
            await session.rollback()
            return print(e)
        
if __name__ == "__main__":
    asyncio.run(create(user_id=2, booK_id=14))