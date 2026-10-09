from pydantic import BaseModel, Field
from typing import Annotated
from fastapi import Depends

class PaginationParams(BaseModel):
    limit: int = Field(5, ge=5, le=100)
    offset: int = Field(0)

PaginationDep = Annotated[PaginationParams, Depends(PaginationParams)]