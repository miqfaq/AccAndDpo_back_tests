from fastapi import APIRouter, Depends, HTTPException, status
from authx import TokenPayload
from src.security.security import security
from src.GigaChatIntegration.databaseWork import get_acc_context, get_att_context
from src.GigaChatIntegration.promptgenerator import prompt_generator

def require_role(*allowed: str):
    async def checker(payload: TokenPayload = Depends(security.access_token_required)):
        role = getattr(payload, "role", None)
        if role not in allowed:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Forbidden")
        return payload
    return checker

router = APIRouter(prefix="/gigachat", tags=["gigachat"])

@router.get('/gigaget')
async def gigachat(attempt_id, acc_id, payload: TokenPayload = Depends(require_role('admin'))):
    acc_context = await get_acc_context(acc_id)
    att_context = await get_att_context(att_id=attempt_id)
    return prompt_generator(acc_context=acc_context, att_context=att_context)
    