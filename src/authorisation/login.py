from src.security.security import config, security
from pydantic import BaseModel
import hashlib, bcrypt, hmac
from src.authorisation.common import get_user_password, get_uid, get_user_role, add_user_role
import jwt
from fastapi import Depends, HTTPException, status
from authx import TokenPayload





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

def get_token(login):
    uid = get_uid(login=login)
    role = get_user_role(uid=str(uid))
    
    token = security.create_access_token(uid=str(uid), data={"role": role})
    return token

def require_role(*allowed: str):
    def checker(payload: TokenPayload = Depends(security.access_token_required)):
        role = getattr(payload, "role", None)
        if role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")
        return payload
    return checker

def add_userRole(uid: str, role: str):
    add_user_role(uid, role)