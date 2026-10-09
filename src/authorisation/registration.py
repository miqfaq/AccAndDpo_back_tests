from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
import bcrypt
from src.authorisation.common import session_factory
from src.authorisation.models import UserData
from src.userPage.models import UserData as UserData_models
import uuid



def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

class UserRegisterSchema(BaseModel):
    uid: uuid.UUID
    login:str
    password:str

def register_user(username: str, password: str) -> bool:
    with session_factory() as session:
        uid = uuid.uuid4()
        user_auth = UserData(uid=uid ,username=username, hash_password=hash_password(password))
        user_info = UserData_models(uid=uid, username=username)
        session.add(user_auth)
        session.add(user_info)
        try:
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False

