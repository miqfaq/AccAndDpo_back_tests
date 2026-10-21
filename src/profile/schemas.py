from pydantic import Field, BaseModel, ConfigDict, BeforeValidator, WithJsonSchema
from typing import Annotated
import json




CONFIG_PATH = "local_cache.json"

class UserDataOut(BaseModel):
    uid: str
    username: str
    firstName: str
    lastName: str
    midName: str
    completedTests: int = Field( )
    totalTests: int
    abc_test_result: int

    model_config = ConfigDict(from_attributes=True)

def _load_levels() -> dict[str, int]:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return {level["name"]: level["max"] for level in data["scale"]["levels"]}

def _load_directions() -> dict[str, str]:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return {direction["name"]: direction["code"] for direction in data["directions"]}

def _load_competencies() -> dict[str, str]:
    with open(CONFIG_PATH, encoding="utf-8") as f:
        data = json.load(f)
    return {skill["name"]: skill["code"] for skill in data["competencies"]}

LEVELS = _load_levels()
_LEVELS_BY_KEY = {name.casefold(): max_ for name, max_ in LEVELS.items()}

def _level_name_to_max(v):
    if not isinstance(v, str):
        raise ValueError("target должен быть строкой")
    try:
        return _LEVELS_BY_KEY[v.casefold()]
    except KeyError:
        raise ValueError(f"Допустимые значения: {', '.join(LEVELS)}")

DIRECTIONS = _load_directions()
_DIRECTIONS = {name.casefold():code for name, code in DIRECTIONS.items()}

def _direction_name_to_code(v):
    if not isinstance(v, str):
        raise ValueError("direction должен быть строкой")
    try:
        return _DIRECTIONS[v.casefold()]
    except KeyError:
        raise ValueError(f"Допустимые значения: {', '.join(DIRECTIONS)}")

COMPETENCIES = _load_competencies()
_COMPETENCIES = {name.casefold():code for name, code in COMPETENCIES.items()}

def _skills_name_to_code(v):
    if not isinstance(v, str):
        raise ValueError("skill должен быть строкой")
    try:
        return _COMPETENCIES[v.casefold()]
    except KeyError:
        raise ValueError(f"Допустимые значения: {', '.join(COMPETENCIES)}")

KeyByCompetencies = Annotated[
    str,
    BeforeValidator(_skills_name_to_code),
    WithJsonSchema({"type": "string", "enum": list(COMPETENCIES)})
]

KeyByDirections = Annotated[
    str,
    BeforeValidator(_direction_name_to_code),
    WithJsonSchema({"type": "string", "enum": list(DIRECTIONS)}),
]

TargetByLevel = Annotated[
    int,
    BeforeValidator(_level_name_to_max),
    WithJsonSchema({"type": "string", "enum": list(LEVELS)}),
]



class AccreditationInput(BaseModel):
    direction: KeyByDirections
    skill: KeyByCompetencies
    target: TargetByLevel
    self_rating: int
    
    
class UserDataIn(BaseModel):
    username: str 
    firstName: str
    lastName: str
    midName: str
    photo: bytes
    accreditations: list[AccreditationInput]
