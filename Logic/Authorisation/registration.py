from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
import bcrypt
from DB.common import session_factory
from DB.models import UserData




def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

class UserRegisterSchema(BaseModel):
    login:str
    password:str

def register_user(username: str, password: str) -> bool:
    with session_factory() as session:
        user = UserData(username=username, hash_password=hash_password(password))
        session.add(user)
        try:
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False

