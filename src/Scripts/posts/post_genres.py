import csv

from app.core.db import Session
from app.models import GenreModel

import asyncio

filepath = "src/Scripts/CSVs/genres.csv"

async def post_genres_from_csv(csv_filepath: str):
    with open(csv_filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            async with Session() as session:
                genre: GenreModel = GenreModel(name=row['name'])
                
                try:
                    session.add(genre)
                    await session.commit()
                    await session.refresh(genre)
                    print(f"Genre {genre.id} - {genre.name} added successfully!")
                    
                except Exception as e:
                    await session.rollback()
                    print(f"Error adding Genre:{genre.name} - Detail: {e}")

    print("All genres created successfully.")
        
if __name__ == "__main__":
    asyncio.run(post_genres_from_csv(csv_filepath=filepath))