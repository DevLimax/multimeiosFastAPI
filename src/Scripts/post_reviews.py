import csv
from app.models import BookReview
from app.core.db import Session
import asyncio

filepath = "src/Scripts/CSVs/reviews.csv"

async def post_reviews_from_csv(csv_filepath: str):
    with open(csv_filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            async with Session() as session:
                    review = BookReview(
                        book_id=int(row['book_id']),
                        user_id=int(row['user_id']),
                        rating=float(row['rating']),
                        comment=row['comment']
                    )
                    try:
                        session.add(review)
                        await session.commit()
                        print(f"Review by {row['user_id']} for book ID {row['book_id']} added successfully.")
                    except Exception as e:
                        await session.rollback()
                        print(f"Failed to add review by {row['user_id']} for book ID {row['book_id']}. Error: {e}")

if __name__ == "__main__":
    asyncio.run(post_reviews_from_csv(filepath))
