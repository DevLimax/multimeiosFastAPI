from sqlmodel import SQLModel

from app.core.db import engine

async def create_tables() -> None:
    import app.models
    print("Creating tables")
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
        
    print("Tables created")
    

if __name__ == "__main__":
    import asyncio

    asyncio.run(create_tables())