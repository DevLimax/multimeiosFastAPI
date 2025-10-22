from app.core.db import Session
from sqlalchemy import select, or_
from app.models.loan_model import LoanModel, Status
from datetime import datetime, timedelta
from app.utils.querys_db import search_all_itens_in_db
import asyncio

async def late_loan_checker() -> None:
    async with Session() as session:
        query = select(LoanModel).filter(LoanModel.status == Status.awaiting_return, LoanModel.return_date > datetime.now())        
        result = await session.execute(query)
        loans = result.scalars().all()
        
        for loan in loans:
            if loan.return_date < datetime.now():
                print(f"O emprestimo de id:{loan.id} está atrasado!")
            else:
                date = loan.return_date - datetime.now()
                print(f"O emprestimo de id:{loan.id} nao esta atrasado!")
                print(f"Dias restantes: {date.days}")
                
if __name__ == "__main__":
    asyncio.run(late_loan_checker())