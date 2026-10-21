from pydantic import Field, BaseModel, ConfigDict, BeforeValidator, WithJsonSchema
from typing import Annotated
from enum import IntEnum
import json
from pathlib import Path


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

LEVELS = _load_levels()
_LEVELS_BY_KEY = {name.casefold(): max_ for name, max_ in LEVELS.items()}

def _level_name_to_max(v):
    if not isinstance(v, str):
        raise ValueError("target должен быть строкой")
    try:
        return _LEVELS_BY_KEY[v.casefold()]
    except KeyError:
        raise ValueError(f"Допустимые значения: {', '.join(LEVELS)}")


TargetByLevel = Annotated[
    int,
    BeforeValidator(_level_name_to_max),
    WithJsonSchema({"type": "string", "enum": list(LEVELS)}),
]


class AccreditationInput(BaseModel):
    direction: str
    skill: str
    target: TargetByLevel
    self_rating: int
    
    
class UserDataIn(BaseModel):
    username: str 
    firstName: str
    lastName: str
    midName: str
    photo: bytes
    accreditations: list[AccreditationInput]
