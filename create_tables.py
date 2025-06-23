from core.configs import settings
from core.db import engine
from sqlalchemy import text

async def create_tables() -> None:
    import models.__all_models
    print("Inicializando criação de tabelas...")

    async with engine.begin() as conn:
        if settings.ENV == "dev":
            print("Ambiente de desenvolvimento detectado. Limpando banco de dados...")
            await conn.execute(text("DROP SCHEMA public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
        else:
            print("Ambiente de produção ou homologação detectado. Apenas criando tabelas se não existirem...")

        await conn.run_sync(settings.DBBASEMODEL.metadata.create_all)

    print("Tabelas criadas com sucesso.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(create_tables())
