from fastapi import APIRouter, Depends, HTTPException
from src.security.security import security
from src.userPage.schemas import UserDataOut
from src.userPage.models import UserData
from src.userPage.databaseWork import get_user_data, update_user_data, delete_user_data, find_user_uid

router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(security.access_token_required)]
)

@router.get('/getuserinfo')
def getUserInfo(uid:str): 
    if not find_user_uid:
        raise HTTPException(status_code=204, detail='No content')
    return get_user_data(uid)
    

@router.patch("/updateUser")
def update_user(userjson: UserDataOut):
    if not find_user_uid:
        raise HTTPException(status_code=204, detail='No content')
    update_user_data(userjson)

@router.delete('/deleteUser')
def delete_user(uid: str):
    if not find_user_uid:
        raise HTTPException(status_code=204, detail='No content')
    delete_user_data(uid)
    