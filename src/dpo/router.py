from fastapi import APIRouter, Depends, HTTPException, status
from authx import TokenPayload
from src.profile.databaseWork import get_user_data, get_accreditations
from src.security.security import security

router = APIRouter(prefix="/dpo", tags=["dpo"])

@router.get("/{user_id}/latest", responses={
        200: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Данные успешно получены",
                        "data": {
                            "userId": "197f66c8-8fd5-459f-8246-271c7dca8211",
                            "fullName": "Kornilov Alexey Dmitrievich",
                            "department": "Dev-dep",
                            "position": "Middle",
                            "area": "Backend",
                            "targetRole": "Senior",
                            "competencies": [
                                {
                                "user_id": "197f66c8-8fd5-459f-8246-271c7dca8211",
                                "uid": "854a4c88-20fd-441f-97bf-fa98d743c3dc",
                                "target": 39,
                                "rating": 17,
                                "direction": "BACKEND",
                                "skill": "PYTHON",
                                "self_rating": 0
                                },
                                {
                                "user_id": "197f66c8-8fd5-459f-8246-271c7dca8211",
                                "uid": "762c0383-cc91-4257-bbef-327aa4b0d865",
                                "target": 69,
                                "rating": 48,
                                "direction": "BACKEND",
                                "skill": "SQL",
                                "self_rating": 12
                                }
                            ]
                        }
                    }
                }
            }
        }
    })
async def get_contract(user_id):
    userinfo = await get_user_data(uid=user_id)
    if userinfo is None:
        raise HTTPException(status_code=204, detail='No content')
    accreditations_list = await get_accreditations(user_id=user_id)
    contract = {
        "userId": f"{user_id}",
        "fullName": f"{userinfo.lastName} {userinfo.firstName} {userinfo.midName}",
        "department": f"{userinfo.department}",
        "position": f"{userinfo.position}",
        "area": f"{userinfo.area}", 
        "targetRole": f"{userinfo.target_role}",
        "competencies": accreditations_list if accreditations_list is not None else None
    }
    return contract
