from sqlmodel import create_engine, Session, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.security.security import settings
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession



# Create the database engine
engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=False, # Set to False in production
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
)

session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass



# def get_session():
#     with Session(engine) as session:
#         try:
#             yield session
#         except Exception:
#             session.rollback()
#             raise