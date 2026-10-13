from pydantic import BaseModel
from typing import Optional, List


class TestUpdateSchema(BaseModel):
    testName: Optional[str] = None
    description: Optional[str] = None

class AnswerCreateSchema(BaseModel):  
    answer_text: str
    answer_is_true: bool = False

class QuestionCreateSchema(BaseModel):
    question_text: str
    answers: List[AnswerCreateSchema]

class TestCreateSchema(BaseModel):
    testName: str
    description: str
    questions: List[QuestionCreateSchema]