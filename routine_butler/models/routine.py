from enum import StrEnum
from typing import List, Optional

from pydantic import BaseModel, constr
from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String

from routine_butler.models.alarm import Alarm
from routine_butler.models.base import BaseDBORMModel, BaseDBPydanticModel


class PriorityLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RoutineElement(BaseModel):
    priority_level: PriorityLevel = PriorityLevel.MEDIUM
    program: str = ""


class RoutineReward(BaseModel):
    program: str = ""


class RoutineORM(BaseDBORMModel):
    """BaseDBORMModel model for a Routine"""

    __tablename__ = "routines"

    TITLE_LENGTH_LIMIT = 60

    title = Column(String(TITLE_LENGTH_LIMIT))
    target_duration_minutes = Column(Integer)
    target_duration_enabled = Column(Boolean)
    elements = Column(JSON)
    rewards = Column(JSON)
    alarms = Column(JSON)
    user_uid = Column(Integer, ForeignKey("users.uid"))


class Routine(BaseDBPydanticModel):
    """BaseDBPydanticModel model for a Routine"""

    title: constr(max_length=RoutineORM.TITLE_LENGTH_LIMIT) = "New Routine"
    target_duration_minutes: int = 30
    target_duration_enabled: bool = False
    elements: List[RoutineElement] = []
    rewards: List[RoutineReward] = []
    alarms: List[Alarm] = []
    user_uid: Optional[int] = None

    class Config:
        orm_model = RoutineORM
