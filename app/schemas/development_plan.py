from datetime import date, datetime
from typing import Annotated, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class InputModel(BaseModel):
    model_config = ConfigDict(extra='forbid', str_strip_whitespace=True)

    @field_validator('*', mode='before')
    @classmethod
    def reject_explicit_null(cls, value, info):
        if value is None and info.field_name not in ('description', 'manager_comment', 'completion_date'):
            raise ValueError('Поле не может быть null')
        return value


Text = Annotated[str, Field(min_length=1)]
ActivityType = Literal['course', 'practice', 'reading']
PlanStatus = Literal['draft', 'pending', 'approved', 'rejected', 'completed']


class DevelopmentPlanReplace(InputModel):
    start_date: date
    end_date: date

    @model_validator(mode='after')
    def check_period(self):
        if self.end_date < self.start_date:
            raise ValueError('Дата окончания не может быть раньше даты начала')
        return self


class DevelopmentPlanCreate(DevelopmentPlanReplace):
    employee_id: int = Field(gt=0)


class DevelopmentPlanUpdate(InputModel):
    start_date: date | None = None
    end_date: date | None = None


class GoalCreate(InputModel):
    description: Text
    deadline: date


class GoalUpdate(InputModel):
    description: Text | None = None
    deadline: date | None = None

    @field_validator('description', mode='before')
    @classmethod
    def description_not_null(cls, value):
        if value is None:
            raise ValueError('Описание не может быть null')
        return value


class ActivityCreate(GoalCreate):
    type: ActivityType


class ActivityUpdate(GoalUpdate):
    type: ActivityType | None = None


class PlanCompetencyUpdate(InputModel):
    current_level: int | None = Field(None, ge=1, le=5)
    target_level: int | None = Field(None, ge=1, le=5)


class PlanCompetencyCreate(InputModel):
    competency_id: int = Field(gt=0)
    current_level: int = Field(ge=1, le=5)
    target_level: int = Field(ge=1, le=5)

    @model_validator(mode='after')
    def check_levels(self):
        if self.target_level < self.current_level:
            raise ValueError('Целевой уровень не может быть ниже текущего')
        return self


class PlanApproveRequest(InputModel):
    manager_comment: str | None = None


class PlanRejectRequest(InputModel):
    manager_comment: Text


class ActivityCompleteRequest(InputModel):
    activity_id: int = Field(gt=0)
    completion_date: date | None = None


class OutputModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ActivityResponse(OutputModel):
    id: int
    goal_id: int
    type: str
    description: str
    deadline: date
    status: str
    completion_date: date | None = None


class GoalWithActivities(OutputModel):
    id: int
    plan_id: int
    description: str
    deadline: date
    activities: list[ActivityResponse] = Field(default_factory=list)
    is_completed: bool


class PlanCompetencyResponse(OutputModel):
    plan_id: int
    competency_id: int
    current_level: int
    target_level: int


class DevelopmentPlanResponse(OutputModel):
    id: int
    employee_id: int
    status: str
    start_date: date
    end_date: date
    manager_comment: str | None = None
    created_at: datetime
    updated_at: datetime
    goals: list[GoalWithActivities] = Field(default_factory=list)
    competencies: list[PlanCompetencyResponse] = Field(default_factory=list)
    progress: float


DevelopmentPlanFullResponse = DevelopmentPlanResponse
