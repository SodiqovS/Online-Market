
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from databases import Database

from ecommerce import config

DATABASE_USERNAME = config.DATABASE_USERNAME
DATABASE_PASSWORD = config.DATABASE_PASSWORD
DATABASE_HOST = config.DATABASE_HOST
DATABASE_NAME = config.DATABASE_NAME

DATABASE_URL = f"postgresql+asyncpg://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_HOST}/{DATABASE_NAME}"

database = Database(DATABASE_URL)

engine = create_async_engine(
            DATABASE_URL,
            future=True,
            pool_pre_ping=True,
            pool_size=20,
            max_overflow=10,
            echo_pool='debug',
            pool_recycle=499,
        )
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


class Base(AsyncAttrs, DeclarativeBase):
    pass


async def get_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()
