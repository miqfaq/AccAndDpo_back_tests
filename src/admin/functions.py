from fastapi import Depends, HTTPException, status
from authx import TokenPayload
from src.security.security import security
from src.database.databaseUse import session_factory
from sqlalchemy import update
from src.authorisation.models import UserAuthData

def require_role(*allowed: str):
    async def checker(payload: TokenPayload = Depends(security.access_token_required)):
        role = getattr(payload, "role", None)
        if role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")
        return payload
    return checker

async def add_user_role(uid: str, role: str):
    async with session_factory() as session:
        stmt = (update(UserAuthData)
                .where(UserAuthData.uid == uid)
                .values(
                    role = role
                ))
        await session.execute(stmt)
        await session.commit()