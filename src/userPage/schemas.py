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
