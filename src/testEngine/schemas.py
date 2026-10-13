from pydantic import BaseModel
import uuid
from typing import List

class AnswerPublic(BaseModel):
    uid: uuid.UUID
    answer_text:str
    model_config = {"from_attributes": True}

class QuestionPublic(BaseModel):
    uid: uuid.UUID
    question_text: str
    answers: List[AnswerPublic]
    model_config = {"from_attributes": True}

class TestPublic(BaseModel):
    uid: uuid.UUID
    testName: str
    description: str
    questions: List[QuestionPublic]

class UserAnswer(BaseModel):
    question_id: uuid.UUID
    answer_ids: List[uuid.UUID]

class SubmitTest(BaseModel):
    answers: List[UserAnswer]

class QuestionResult(BaseModel):
    question_id: uuid.UUID
    is_correct: bool
    correct_answer_ids: List[uuid.UUID]

class TestResult(BaseModel):
    total: int
    correct: int
    percent: float
    details: List[QuestionResult]
