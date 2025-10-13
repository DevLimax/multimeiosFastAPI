from sqlmodel import select
from sqlalchemy.orm import joinedload, DeclarativeMeta
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.configs import settings
from fastapi import Response, status
from typing import Optional, Type

async def search_item_in_db(id: int, 
                            Model: Type[DeclarativeMeta], 
                            session: AsyncSession, 
):
    """
    Função para buscar um item no banco de dados pelo ID.
    """
    query = select(Model).filter(Model.id == id )
    result = await session.execute(query)
    item = result.scalars().unique().one_or_none()
    return item

async def search_all_itens_in_db(
    Model: Type[DeclarativeMeta], 
    session: AsyncSession
):
    """
    Função para buscar todos os itens de um modelo no banco de dados.
    """
    query = select(Model).order_by(Model.id)
    result = await session.execute(query)
    list_itens = result.scalars().unique().all()
    return list_itens
    
    

