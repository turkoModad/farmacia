import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from app.variables import USER_DATABASE_URL, DATABASE_URL


logger = logging.getLogger("DatabaseAsync")

logger.info(f"Inicializando motor asíncrono.")


engine = create_async_engine(
    USER_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=5,
    pool_timeout=30,
    pool_recycle=1200
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


engine_sync = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)