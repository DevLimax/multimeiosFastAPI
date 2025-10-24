from random import randint
from typing import List, Optional
from app.core.db import Session
from app.models import LoanRequestModel, UserModel, BookModel
from app.utils.querys_db import search_all_itens_in_db
import asyncio

filepath_base = 'src/Scripts/CSVs/requests.csv'

async def post_requests():
    async with Session() as session:
        users: List[UserModel] = await search_all_itens_in_db(Model=UserModel,
                                                              session=session)
        books: List[BookModel] = await search_all_itens_in_db(Model=BookModel,
                                                              session=session)
        
        for user in users:
            request = LoanRequestModel(user_id=user.id,
                             book_id=books[randint(0, 29)].id)
            try:
                session.add(request)
                await session.commit()
                await session.refresh(request)
                print(f"Request: {request.id} - added successfully in db")
            except Exception as e:
                await session.rollback()
                print(f"Error adding Request:{request.id} - Detail: {e}")
            finally:
                await session.close()
            
                    
    print("All loan requests added successfully.")

if __name__ == "__main__":
    asyncio.run(post_requests())