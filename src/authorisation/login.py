from src.security.security import config, security
from pydantic import BaseModel, EmailStr
import hashlib, bcrypt, hmac
from src.authorisation.common import get_user_password, get_uid, get_user_role, add_user_role
import jwt
from fastapi import Depends, HTTPException, status
from authx import TokenPayload

cookie = config.JWT_ACCESS_COOKIE_NAME

async def verify_password(password: str, stored: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), stored.encode("utf-8"))

class UserLoginSchema(BaseModel):
    login: EmailStr
    password: str

async def is_verified(login: str, password: str):
    stored_pwd = await get_user_password(login=login)
    if stored_pwd is not None:
        return await verify_password(password=password, stored=stored_pwd) 
    else:
        return False

async def get_token(login):
    uid = await get_uid(login=login)
    role = await get_user_role(uid=str(uid))
    
    token = security.create_access_token(uid=str(uid), data={"role": role})
    return token

def require_role(*allowed: str):
    async def checker(payload: TokenPayload = Depends(security.access_token_required)):
        role = getattr(payload, "role", None)
        if role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")
        return payload
    return checker

async def add_userRole(uid: str, role: str):
    await add_user_role(uid, role)