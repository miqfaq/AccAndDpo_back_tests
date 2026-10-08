from authx import AuthX, AuthXConfig
from pydantic import BaseModel
import hashlib, bcrypt, hmac
from DB.common import get_user_password
from Logic.Authorisation.registration import hash_password

config = AuthXConfig()
config.JWT_SECRET_KEY = "SK"
config.JWT_ACCESS_COOKIE_NAME = "MAT"
config.JWT_TOKEN_LOCATION = ['cookies']

security = AuthX(config=config)
auth_token = security.create_access_token(uid="123")
cookie = config.JWT_ACCESS_COOKIE_NAME

def verify_password(password: str, stored: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), stored.encode("utf-8"))

class UserLoginSchema(BaseModel):
    username: str
    password: str

def is_verified(login: str, password: str):
    stored_pwd = get_user_password(login=login)
    if stored_pwd is not None:
        return verify_password(password=password, stored=stored_pwd) 
    else:
        return False