from fastapi import APIRouter, Depends
from src.security.security import security
from authx import TokenPayload
from src.authorisation.login import require_role


router = APIRouter(
    prefix="/tests",
    tags=["testPage"]
    )



@router.get('/', dependencies=[Depends(security.access_token_required)])
def get_test_list(uid: str):
    pass

@router.patch('/patch')
def patch_test_list( payload: TokenPayload = Depends(require_role('admin'))):
    pass

@router.post("/newpostlist")
def new_post_list(payload: TokenPayload = Depends(require_role('admin'))):
    pass

@router.delete("/deletetestlist")
def delete_post_list(payload: TokenPayload = Depends(require_role('admin'))):
    pass