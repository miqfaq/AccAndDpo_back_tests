from sqlmodel import create_engine, Session, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from src.security.security import settings



# Create the database engine
engine = create_engine(
    url=settings.DATABASE_URL,
    echo=False, # Set to False in production
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
)

session_factory = sessionmaker(engine)

class Base(DeclarativeBase):
    pass



# def get_session():
#     with Session(engine) as session:
#         try:
#             yield session
#         except Exception:
#             session.rollback()
#             raise