import csv
from app.core.db import Session
from app.models.user_model import UserModel
from app.core.security import generate_hashed_password
import asyncio

async def post_users_from_csv(csv_filepath):
    with open(csv_filepath, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        for row in reader:
            async with Session() as session:
                user: UserModel = UserModel(first_name=row['first_name'],
                                            last_name=row['last_name'],
                                            enrollment=int(row['enrollment']),
                                            email=row['email'],
                                            password=generate_hashed_password(row['password']),
                                            is_admin=bool(row['is_admin']),
                                            is_active=True)
                
                try:
                    session.add(user)
                    await session.commit()
                    await session.refresh(user)
                    print(f"User: {user.id}-{user.first_name} added successfully in db")
                except Exception as e:
                    await session.rollback()
                    print(f"Error adding User:{user.first_name} - Detail: {e}")
                finally:
                    await session.close()

    print("All users created successfully.")

if __name__ == "__main__":
    asyncio.run(post_users_from_csv(csv_filepath="src/Scripts/CSVs/users.csv"))
    