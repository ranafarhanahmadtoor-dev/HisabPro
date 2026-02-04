from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from .config import settings

# SQLite for Dev, easily swappable for Postgres via Env Var
DATABASE_URL = settings.DATABASE_URL

# SQLAlchemy engine configuration
if DATABASE_URL.startswith("sqlite"):
    engine = create_async_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool # Needed for simple file-based sqlite in async
    )
else:
    engine = create_async_engine(DATABASE_URL)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with SessionLocal() as session:
        yield session
