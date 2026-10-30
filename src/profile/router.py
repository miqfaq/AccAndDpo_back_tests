from fastapi import APIRouter, Depends, HTTPException
from src.security.security import security, TokenPayload
from src.profile.schemas import UserDataOut, AccreditationInput
from src.profile.models import UserData
from src.profile.databaseWork import get_user_data, update_user_data, delete_user_data, find_user_uid, add_accreditation, get_accreditations
import json


router = APIRouter(
    prefix="/profile",
    tags=["profile"],
    dependencies=[Depends(security.access_token_required)]
)

@router.get('/getuserinfo')
def getUserInfo(uid:str): 
    if not find_user_uid(uid):
        raise HTTPException(status_code=204, detail='No content')
    return get_user_data(uid)
    
@router.patch("/updateUser")
def update_user(userjson: UserDataOut):
    if not find_user_uid(userjson.uid):
        raise HTTPException(status_code=204, detail='No content')
    update_user_data(userjson)

@router.delete('/deleteUser')
def delete_user(uid: str):
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



@router.get("/{user_id}/latest")
def post_contract(user_id):
    userinfo = get_user_data(uid=user_id)
    if userinfo is None:
        raise HTTPException(status_code=204, detail='No content')
    accreditations_list = get_accreditations(user_id=user_id)
    contract = {
        "userId": "...",
        "fullName": f"{userinfo.lastName} {userinfo.firstName} {userinfo.midName}",
        "department": f"{userinfo.department}",
        "position": f"{userinfo.position}",
        "area": f"{userinfo.area}", 
        "targetRole": f"{userinfo.target_role}",
        "competencies": accreditations_list
    }
