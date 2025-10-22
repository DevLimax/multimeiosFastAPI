from datetime import datetime, timedelta
import csv
from random import randint
from app.core.db import Session
from app.models import LoanRequestModel
import asyncio

filepath_base = 'src/Scripts/CSVs/requests.csv'

async def post_requests_from_csv(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            row['created_at'] = datetime.now() + timedelta(days=randint(1, 30))
            async with Session() as session:
                loan_request = LoanRequestModel(
                    user_id=int(row['user_id']),
                    book_id=int(row['book_id']),
                    created_at=row['created_at']
                )
                try:
                    session.add(loan_request)
                    await session.commit()
                    print(f"Loan request added: {loan_request.id}")
                except Exception as e:
                    await session.rollback()
                    print(f"Error occurred: {e}")
                    
    print("All loan requests added successfully.")

if __name__ == "__main__":
    asyncio.run(post_requests_from_csv(filepath_base))