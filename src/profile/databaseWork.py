from src.profile.models import UserData, Accreditation
from src.profile.schemas import UserDataOut, AccreditationInput
from src.authorisation.models import UserAuthData as UserAuthData
from src.database.databaseUse import session_factory
from sqlalchemy import select, update, delete

async def get_user_data(uid):
    async with session_factory() as session:
        stmt = select(UserData).where(UserData.uid == uid)
        res = await session.execute(stmt)
        user = res.scalars().one_or_none()
        return user

async def update_user_data(userjson, user_id):
    
    async with session_factory() as session:
        stmt = (
            update(UserData)
            .where(UserData.uid == user_id)
            .values(
                username = userjson.username,
                firstName = userjson.firstName,
                lastName = userjson.lastName,
                midName = userjson.midName,
                department = userjson.department,
                photo = userjson.photo,
                position = userjson.position,
                area = userjson.area,
                target_role = userjson.target_role
            )
        )
        await session.execute(stmt)
        await session.commit()

async def delete_user_data(uid: str):
    async with session_factory() as session:
        stmt = (
            delete(UserData)
            .where(UserData.uid == uid)
        )
        stmt2 = (
            delete(UserAuthData)
            .where(UserAuthData.uid == uid)
        )
        stmt3 = (
            delete(Accreditation)
            .where(Accreditation.user_id == uid)
        )
        await session.execute(stmt)
        await session.execute(stmt2)
        await session.execute(stmt3)
        await session.commit()

async def find_user_uid(uid: str):
    async with session_factory() as session:
        stmt = select(UserData).where(UserData.uid == uid)
        stmt2 = select(UserAuthData).where(UserAuthData.uid == uid)
        response1 = await session.execute(stmt)
        response2 = await session.execute(stmt2)
        userdatauid = response1.scalars().one_or_none()
        userauthuid = response2.scalars().one_or_none()
        if (userauthuid is not None) and (userdatauid is not None):
            print(userauthuid, userdatauid)
            return userauthuid.uid == userdatauid.uid
        raise ValueError("userdatauid or userauthuid is none")

async def add_self_rating(user_id, self_rating, accreditation_id):
    async with session_factory() as session:
        accreditation = await session.scalar(
            select(Accreditation)
            .where(Accreditation.user_id == user_id and Accreditation.uid == accreditation_id)
        )
        if accreditation is None:
            raise ValueError("Accreditation not found")
        acc = accreditation.self_rating = self_rating
        session.add(acc)
        await session.commit()

async def add_accreditation(accreditation_input:AccreditationInput, uid:str):
    async with session_factory() as session:
        accreditation = Accreditation(
            user_id = uid,
            direction = accreditation_input.direction,
            skill = accreditation_input.skill,
            target = accreditation_input.target,
            self_rating = accreditation_input.self_rating
            )
        session.add(accreditation)
        await session.commit()

async def get_accreditations(user_id):
    async with session_factory() as session:
        stmt = (
            select(Accreditation)
            .where(Accreditation.user_id == user_id)
        )
        res = await session.execute(stmt)
        return res.scalars().all()

