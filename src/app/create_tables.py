from app.core.configs import settings
from sqlalchemy.engine import Engine

from app.core.db import engine

async def create_tables(engine: Engine) -> None:
    import app.models
    print("Creating tables")
    
    async with engine.begin() as conn:
        await conn.run_sync(settings.DBBASEMODEL.metadata.drop_all)
        await conn.run_sync(settings.DBBASEMODEL.metadata.create_all)
        
    print("Tables created")
    

def create_tables_test(engine: Engine) -> None:
    import app.models
    print("Creating tables for test")

    with engine.begin() as conn:
        settings.DBBASEMODEL.metadata.drop_all(bind=engine)
        settings.DBBASEMODEL.metadata.create_all(bind=engine)

    print("Test tables created")

if __name__ == "__main__":
    import asyncio

    asyncio.run(create_tables())