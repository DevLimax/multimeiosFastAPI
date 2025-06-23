from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.configs import settings

async def search_item_in_db(id: int, Model: settings.DBBASEMODEL, db: AsyncSession):
    async with db as session:
        query = select(Model).filter(Model.id == id )
        result = await session.execute(query)
        item = result.scalars().unique().one_or_none()
        return item
