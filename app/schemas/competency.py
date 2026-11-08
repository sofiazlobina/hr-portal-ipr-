from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.schemas.development_plan import InputModel


class CompetencyCreate(InputModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = None


class CompetencyUpdate(InputModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None


class CompetencyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: str | None = None
