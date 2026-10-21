from fastapi import APIRouter, Depends, HTTPException
from src.security.security import TokenPayload, security
from src.testEngine.databaseWork import get_direction, getTest, addQuestion
from src.testEngine.schemas import QuestionShcema
from src.authorisation.login import require_role
import uuid

router = APIRouter(
    prefix="/test_engine",
    tags=['test_engine']
)

@router.get("/accreditation_get_direction")
def accreditation_get_direction(acc_id:str, payload: TokenPayload = Depends(security.access_token_required)):
    direction = get_direction(acc_id=acc_id, user_id=payload.sub)
    return direction

@router.get("/test_generatre")
def get_test(accId, payload: TokenPayload = Depends(security.access_token_required)):
    return getTest(userId=uuid.UUID(payload.sub), acc_id=accId)

@router.post("/addQuestion")
def add_question(question_list: list[QuestionShcema], payload: TokenPayload=Depends(require_role("manager", "admin"))):
    for question in question_list:
        addQuestion(question=question)