from fastapi import APIRouter, Depends, HTTPException, status
from authx import TokenPayload
from src.security.security import security
from src.admin.functions import require_role, add_user_role



router = APIRouter(prefix="/admin", tags=['admin'])

@router.post('/addRole')
def add_role (uid, role, payload: TokenPayload = Depends(require_role('admin'))):
    add_user_role(uid, role)
