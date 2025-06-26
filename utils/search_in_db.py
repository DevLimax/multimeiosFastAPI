from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.configs import settings
from .exceptionsHttp import not_found 
from fastapi import Response, status

async def search_item_in_db(id: int, Model: settings.DBBASEMODEL, db: AsyncSession):
    """
    Função para buscar um item no banco de dados pelo ID.
    """
    query = select(Model).filter(Model.id == id )
    result = await db.execute(query)
    item = result.scalars().unique().one_or_none()
    return item

async def search_all_itens_in_db(Model: settings.DBBASEMODEL, db: AsyncSession):
    """
    Função para buscar todos os itens de um modelo no banco de dados.
    """
    query = select(Model).order_by(Model.id)
    result = await db.execute(query)
    list_itens = result.scalars().unique().all()
    return list_itens
    

        
