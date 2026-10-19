from src.profile.models import UserData, Accreditation
from src.profile.schemas import UserDataOut, AccreditationInput
from src.authorisation.models import UserAuthData as UserAuthData
from src.database.databaseUse import session_factory
from sqlalchemy import select, update, delete

def get_user_data(uid):
    with session_factory() as session:
        stmt = select(UserData).where(UserData.uid == uid)
        user = session.scalars(stmt).one_or_none()
        return user

def update_user_data(userjson):
    valid_data = UserDataOut.model_validate(userjson)
    with session_factory() as session:
        uid = valid_data.uid
        stmt = (
            update(UserData)
            .where(UserData.uid == uid)
            .values(
                username = valid_data.username,
                firstName = valid_data.firstName,
                lastName = valid_data.lastName,
                midName = valid_data.midName,
                completedTests = valid_data.completedTests,
                totalTests = valid_data.totalTests,
                abc_test_result = valid_data.abc_test_result
            )
        )
        session.execute(stmt)
        session.commit()

def delete_user_data(uid: str):
    with session_factory() as session:
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
        session.execute(stmt)
        session.execute(stmt2)
        session.execute(stmt3)
        session.commit()

def find_user_uid(uid: str):
    with session_factory() as session:
        stmt = select(UserData).where(UserData.uid == uid)
        stmt2 = select(UserAuthData).where(UserAuthData.uid == uid)
        userdatauid = session.scalars(stmt).one_or_none()
        userauthuid = session.scalars(stmt2).one_or_none()
        if (userauthuid is not None) and (userdatauid is not None):
            print(userauthuid, userdatauid)
            return userauthuid.uid == userdatauid.uid
        raise ValueError("userdatauid or userauthuid is none")

def add_self_rating(user_id, self_rating, accreditation_id):
    with session_factory() as session:
        accreditation = session.scalar(
            select(Accreditation)
            .where(Accreditation.user_id == user_id and Accreditation.uid == accreditation_id)
        )
        if accreditation is None:
            raise ValueError("Accreditation not found")
        acc = accreditation.self_rating = self_rating
        session.add(acc)
        session.commit()
        ret = session.refresh(acc)
        return ret

def add_accreditation(accreditation_input:AccreditationInput, uid:str):
    with session_factory() as session:
        accreditation = Accreditation(
            user_id = uid,
            direction = accreditation_input.direction,
            skill = accreditation_input.skill,
            ability = accreditation_input.ability,
            target = accreditation_input.target,
            self_rating = accreditation_input.self_rating
            )
        session.add(accreditation)
        session.commit()

