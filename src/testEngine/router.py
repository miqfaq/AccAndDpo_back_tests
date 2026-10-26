from fastapi import APIRouter, Depends, HTTPException
from src.security.security import TokenPayload, security
from src.testEngine.databaseWork import get_direction, getTest, addQuestion, getAccList_uid, save_attempt, score_count, rating_count
from src.testEngine.schemas import QuestionShcema, AttemptSchema
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

@router.get("/getAcclist")
def get_acc_list(payload: TokenPayload = Depends(security.access_token_required)):
    return getAccList_uid(uid=uuid.UUID(payload.sub))

@router.post("/submitattempt")
def submitAttempt(attempt: AttemptSchema, accreditation_id, payload: TokenPayload = Depends(security.access_token_required)):
    save_attempt(attempt=attempt, user_id=uuid.UUID(payload.sub), accreditation_id=accreditation_id)
    score_count(user_id=uuid.UUID(payload.sub), acc_id=accreditation_id)
    print(f'SKILL{attempt.skill}')
    rating_count(user_id=uuid.UUID(payload.sub), skill=attempt.skill)
    