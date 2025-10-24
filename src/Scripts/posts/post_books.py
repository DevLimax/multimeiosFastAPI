import csv

from app.core.db import Session
from app.models import BookModel

import asyncio

filepath = "src/Scripts/CSVs/books.csv"

async def post_books_from_csv(csv_filepath: str):
    with open(csv_filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            async with Session() as session:
                book: BookModel = BookModel(title=row['title'],
                                            author=row['author'],
                                            genre_id=int(row['genre_id']),
                                            genre_two_id=int(row['genre_two_id']) if row['genre_two_id'] else None,
                                            quantity=int(row['quantity']),
                                            synopsis=row['synopsis'],
                                            added_by_id=20)
            
            try:
                session.add(book)
                await session.commit()
                await session.refresh(book)
                print(f"User: {book.id}-{book.title} added successfully in db")
                
            except Exception as e:
                
                await session.rollback()
                print(f"Error adding User:{book.title} - Detail: {e}")

    print("All books created successfully.")
    
if __name__ == "__main__":
    asyncio.run(post_books_from_csv(csv_filepath=filepath))