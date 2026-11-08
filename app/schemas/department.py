from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Название отдела")


class DepartmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)


class DepartmentResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)