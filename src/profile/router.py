from fastapi import APIRouter, Depends, HTTPException, Body
from typing import Annotated
from src.security.security import security, TokenPayload
from src.profile.schemas import UserDataOut, AccreditationInput, UserContract
from src.profile.models import UserData
from src.profile.databaseWork import get_user_data, update_user_data, delete_user_data, find_user_uid, add_accreditation, get_accreditations
import json


router = APIRouter(
    prefix="/profile",
    tags=["profile"],
    dependencies=[Depends(security.access_token_required)]
)

@router.get('/getuserinfo', responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Данные успешно получены",
                        "data": {
                            "lastName": "Kornilov",
                            "uid": "197f66c8-8fd5-459f-8246-271c7dca8211",
                            "department": "Dev-dep",
                            "area": "Backend",
                            "username": "miqfaq",
                            "firstName": "Alexey",
                            "midName": "Dmitrievich",
                            "position": "Middle",
                            "target_role": "Senior"
                            }
                        }
                    }
                }
            }
        }
    )
def getUserInfo(payload: TokenPayload = Depends(security.access_token_required)): 
    uid = payload.sub
    if not find_user_uid(uid):
        raise HTTPException(status_code=204, detail='No content')
    return get_user_data(uid)
    
@router.patch("/updateUser")
def update_user(userjson: UserDataOut, payload: TokenPayload = Depends(security.access_token_required)):
    uid = payload.sub
    if not find_user_uid(uid):
        raise HTTPException(status_code=204, detail='No content')
    update_user_data(userjson, uid)

@router.delete('/deleteUser')
def delete_user(payload: TokenPayload = Depends(security.access_token_required)):
    uid = payload.sub
    if not find_user_uid(uid):
        raise HTTPException(status_code=204, detail='No content')
    delete_user_data(uid)

@router.post("/addAcc")
def add_accreditation_to_profile(acc: AccreditationInput, payload: TokenPayload = Depends(security.access_token_required)):
    uid = payload.sub
    if not find_user_uid(uid):
        raise HTTPException(status_code=204, detail='No content')
    add_accreditation(acc, uid)
    return "sucess"

@router.get('/getAccType')
def get_acc_type_from_cache():
    with open("local_cache.json", 'r', encoding='utf-8') as file:
        js = json.load(file)
        return js["competencies"]

