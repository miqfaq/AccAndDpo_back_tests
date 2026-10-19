from src.authorisation.models import UserAuthData
from src.database.databaseUse import session_factory
from sqlalchemy import select, update

def insert_user_reg_data(username: str, hash_password:str):
    user = UserAuthData(username=username, hash_password=hash_password)
    with session_factory() as session:
        session.add(user)
        session.commit()

def get_user_reg_login():
    with session_factory() as session:
        login = session.query(UserAuthData.username).all()
        return login

def get_user_password(login: str):
    with session_factory() as session:
        stmt = select(UserAuthData.hash_password).where(UserAuthData.username == login)
        hash_pwd = session.scalar(stmt)
        return hash_pwd

def get_uid(login:str):
    with session_factory() as session:
        stmt = select(UserAuthData.uid).where(UserAuthData.username == login)
        uid = session.scalar(stmt)
        return uid

def get_user_role(uid:str):
    with session_factory() as session:
        stmt = select(UserAuthData.role).where(UserAuthData.uid == uid)
        role = session.scalar(stmt)
        return role

def add_user_role(uid: str, role: str):
    with session_factory() as session:
        stmt = (update(UserAuthData)
                .where(UserAuthData.uid == uid)
                .values(
                    role = role
                ))
        session.execute(stmt)
        session.commit()