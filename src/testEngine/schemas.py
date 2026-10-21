from pydantic import Field, BaseModel, BeforeValidator, WithJsonSchema
from typing import Annotated
from src.profile.schemas import KeyByDirections, KeyByCompetencies
import uuid
import json
from enum import StrEnum

CONFIG_PATH = "local_cache.json"

def _load_skills() -> dict[str, str]:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return {
        skill["name"]: skill["code"]
        for competency in data["competencies"]
        for skill in competency["skills"]
    }

SKILLS = _load_skills()
_SKILLS = {name.casefold(): code for name, code in SKILLS.items()}

def _skill_name_to_code(v):
    if not isinstance(v, str):
        raise ValueError("skill должен быть строкой")
    try:
        return _SKILLS[v.casefold()]
    except KeyError:
        raise ValueError(f"Допустимые значения: {', '.join(SKILLS)}")

KeyBySkill = Annotated[
    str,
    BeforeValidator(_skill_name_to_code),
    WithJsonSchema({"type": "string", "enum": list(SKILLS)})
]


class AnswerSchema(BaseModel):
    answer_text: str
    is_true: bool = Field(default=False)
    answer_id: uuid.UUID

class QuestionShcema(BaseModel):
    question_text: str
    answer_list: list[AnswerSchema]
    question_id: uuid.UUID
    difficulty: int = Field(default=1)
    direction: KeyByDirections
    skill: KeyByCompetencies
    ability: KeyBySkill

class GetTestSchema(BaseModel):
    user_id: uuid.UUID
    acc_id: uuid.UUID

class Direction(StrEnum):
    backend = "BACKEND"
    frontend = "FRONTEND"
    sql = "SQL"
    default = "default"
    

    