from fastapi import APIRouter, Depends, HTTPException
from src.security.security import TokenPayload, security
from src.testEngine.databaseWork import get_direction

router = APIRouter(
    prefix="/test_engine",
    tags=['test_engine']
)

@router.get("/accreditation_get_direction")
def accreditation_get_direction(acc_id:str, payload: TokenPayload = Depends(security.access_token_required)):
    direction = get_direction(acc_id=acc_id, user_id=payload.sub)
    return direction