from sqlmodel import create_engine, Session, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_USERNAME = "postgres"
PASSWORD = "12345"
DATABASE_HOST = "127.0.0.1"
DATABASE_PORT = "5432"
DATABASE_NAME = "AccAndDpo_test_back"

DATABASE_URL = f"postgresql+psycopg://{DATABASE_USERNAME}:{PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

# Create the database engine
engine = create_engine(
    url=DATABASE_URL,
    echo=True, # Set to False in production
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
)

with engine.connect() as conn:
    res = conn.execute(text('SELECT VERSION()'))
    print(f"{res.all()=}")

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