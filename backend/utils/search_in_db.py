from sqlalchemy.future import select
from sqlalchemy.orm import DeclarativeMeta
from sqlalchemy.ext.asyncio import AsyncSession
from core.configs import settings
from typing import Optional, Type
from datetime import datetime

async def search_item_in_db(id: int, 
                            Model: Type[DeclarativeMeta], 
                            db: AsyncSession,
):
    """
    Função para buscar um item no banco de dados pelo ID.
    """ 
    query = select(Model).filter(Model.id == id )
    result = await db.execute(query)
    item = result.scalars().unique().one_or_none()
    return item

async def search_all_itens_in_db(Model: Type[DeclarativeMeta], 
                                 db: AsyncSession,
                                 filters: Optional[dict] = None
):
    """
    Função para buscar todos os itens de um modelo no banco de dados.
    """
    query = select(Model).order_by(Model.id)
    
    if filters: 
        
        if filters.start_date and filters.end_date:
            start_date = filters.start_date 
            end_date = filters.end_date
            query = query.where(Model.created_at.between(start_date, end_date))
        elif filters.start_date:
            start_date = filters.start_date
            query = query.where(Model.created_at >= start_date)
        elif filters.end_date:
            end_date = filters.end_date
            query = query.where(Model.created_at <= end_date)
            
        for atrr, value in filters.dict(exclude_none=True).items():
            try:
                column = getattr(Model, atrr)
            except AttributeError:
                continue
            if column is not None:
                if isinstance(value, str):
                    if column == Model.status:
                        query = query.where(column == value)
                    else:
                        query = query.where(column.ilike(f"%{value}%"))
                else:
                    query = query.where(column == value)
                
    result = await db.execute(query)
    list_itens = result.scalars().unique().all()
    return list_itens
    
    

        
