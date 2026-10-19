from pydantic import Field, BaseModel, ConfigDict

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


class AccreditationInput(BaseModel):
    direction: str
    skill: str
    ability: str
    target: int
    self_rating: int

    
class UserDataIn(BaseModel):
    username: str 
    firstName: str
    lastName: str
    midName: str
    photo: bytes
    accreditations: list[AccreditationInput]
