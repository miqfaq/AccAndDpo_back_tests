from src.authorisation.models import UserAuthData
from src.database.databaseUse import session_factory
from sqlalchemy import select, update

async def insert_user_reg_data(username: str, hash_password:str):
    user = UserAuthData(username=username, hash_password=hash_password)
    async with session_factory() as session:
        session.add(user)
        await session.commit()

async def get_user_password(login: str):
    async with session_factory() as session:
        stmt = select(UserAuthData.hash_password).where(UserAuthData.login == login)
        hash_pwd = await session.scalar(stmt)
        return hash_pwd

async def get_uid(login:str):
    async with session_factory() as session:
        stmt = select(UserAuthData.uid).where(UserAuthData.login == login)
        uid = await session.scalar(stmt)
        return uid

async def get_user_role(uid:str):
    async with session_factory() as session:
        stmt = select(UserAuthData.role).where(UserAuthData.uid == uid)
        role = await session.scalar(stmt)
        return role

async def add_user_role(uid: str, role: str):
    async with session_factory() as session:
        stmt = (update(UserAuthData)
                .where(UserAuthData.uid == uid)
                .values(
                    role = role
                ))
        await session.execute(stmt)
        await session.commit()