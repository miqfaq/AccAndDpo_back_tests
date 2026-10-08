from .models import UserData
from DB.databaseUse import session_factory
from sqlalchemy import select

def insert_user_reg_data(username: str, hash_password:str):
    user = UserData(username=username, hash_password=hash_password)
    with session_factory() as session:
        session.add(user)
        session.commit()

def get_user_reg_login():
    with session_factory() as session:
        login = session.query(UserData.username).all()
        return login

def get_user_password(login: str):
    with session_factory() as session:
        stmt = select(UserData.hash_password).where(UserData.username == login)
        hash_pwd = session.scalar(stmt)
        return hash_pwd