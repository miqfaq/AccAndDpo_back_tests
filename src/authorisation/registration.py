from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel, EmailStr
import bcrypt
from src.authorisation.common import session_factory
from src.authorisation.models import UserAuthData
from src.profile.models import UserData as UserData_models
import uuid



async def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

class UserRegisterSchema(BaseModel):
    uid: uuid.UUID
    login: EmailStr
    password:str

async def register_user(username: str, password: str) -> bool:
    async with session_factory() as session:
        uid = uuid.uuid4()
        user_auth = UserAuthData(uid=uid , login=username, hash_password= await hash_password(password))
        user_info = UserData_models(uid=uid, login=username)
        session.add(user_auth)
        session.add(user_info)
        try:
            await session.commit()
            return True
        except IntegrityError:
            await session.rollback()
            return False

