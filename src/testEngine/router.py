import uuid
from fastapi import APIRouter, HTTPException
from src.testEngine.schemas import TestPublic, TestResult, SubmitTest
from src.testEngine.databaseWork import get_test_for_passing, check_test


router = APIRouter(
    prefix='/testengine',
    tags=['testengine']
)


@router.post('/{test_uid}', response_model=TestPublic)
def start_test(test_uid: uuid.UUID):
    test = get_test_for_passing(test_uid)
    if test is None:
        raise HTTPException(404, "Test not found")
    return test

@router.post("/tests/{test_uid}/submit", response_model=TestResult)
def submit_test(test_uid: uuid.UUID, body: SubmitTest):
    return check_test(test_uid, body)