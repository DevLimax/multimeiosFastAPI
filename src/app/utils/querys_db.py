from sqlalchemy import select, or_
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
    session: AsyncSession,
    filters: Optional[dict] = None
):
    """
    Função para buscar todos os itens de um modelo no banco de dados.
    """
    
    query = select(Model).order_by(Model.id)
    
    print(filters)
    if filters:

        if Model.__tablename__ == "usuarios" and filters.name:
            query = query.filter(or_(
                Model.first_name.ilike(f"%{filters.name}%"),
                Model.last_name.ilike(f"%{filters.name}%")
            ))
            
        if Model.__tablename__ == "livros" and filters.genre_id:
            query = query.filter(or_(
                Model.genre_id == filters.genre_id,
                Model.genre_two_id == filters.genre_id
            ))

        if Model.__tablename__ == "avaliacoes" and (filters.max_rating or filters.min_rating):
            if filters.max_rating and filters.min_rating:
                query = query.where(Model.rating.between(filters.min_rating, filters.max_rating))
            elif filters.max_rating:
                query = query.where(Model.rating <= filters.max_rating)
            elif filters.min_rating:
                query = query.where(Model.rating >= filters.min_rating)

        if Model.__tablename__ == "emprestimos" or Model.__tablename__ == "solicitacoes_emprestimos" or Model.__tablename__ == "avaliacoes":
            if filters.start_date or filters.end_date:
                if filters.start_date and filters.end_date:
                    query = query.where(Model.created_at.between(filters.start_date, filters.end_date))
                elif filters.start_date:
                    query = query.where(Model.created_at >= filters.start_date)
                elif filters.end_date:
                    query = query.where(Model.created_at <= filters.end_date)
            
        for atrr, value in filters.dict(exclude_none=True).items():
            if atrr == "genre_id":
                continue
            
            try: 
                column = getattr(Model, atrr)
            except AttributeError:
                continue
            
            if column is not None:
                if isinstance(value, str) and atrr != "status":
                    query = query.where(column.ilike(f"%{value}%"))
                else:
                    query = query.where(column == value)
            
    
    result = await session.execute(query)
    list_itens = result.scalars().unique().all()
    return list_itens
    
    

