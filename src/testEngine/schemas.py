from pydantic import Field, BaseModel, ConfigDict
import uuid

class AnswerSchema(BaseModel):
    answer_text: str
    is_true: bool = Field(default=False)
    answer_id: uuid.UUID

class QuestionShcema(BaseModel):
    question_text: str
    answer_list: list[AnswerSchema]
    question_id: uuid.UUID
    difficulty: int = Field(default=1)
