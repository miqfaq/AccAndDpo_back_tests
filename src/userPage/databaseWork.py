from src.userPage.models import UserData
from src.userPage.schemas import UserDataOut
from src.authorisation.models import UserData as UserAuthData
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
        session.execute(stmt)
        session.execute(stmt2)
        session.commit()

def find_user_uid(uid: str):
    with session_factory() as session:
        stmt = select(UserData).where(UserData.uid == uid)
        stmt2 = select(UserAuthData).where(UserAuthData.uid == uid)
        userdatauid = session.scalars(stmt).one_or_none()
        userauthuid = session.scalars(stmt2).one_or_none()
        return userauthuid == userdatauid
