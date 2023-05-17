from enum import StrEnum
from typing import List, Optional, TypedDict

from pydantic import constr
from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String

from routine_butler.models.base import BaseDBORMModel, BaseDBPydanticModel

# NOTE: the reason why Alarm and RoutineElement are not their own tables in the
# db is simply *PERSONAL PREFERENCE* based loosely on the following:

# - RoutineElement: removes need manage bi-parental foreign keys to Routine & Program
# - Alarm: consistency w/ RoutineElement


class RingFrequency(StrEnum):
    "Enum for a Alarm's sound frequency"
    CONSTANT = "constant"
    PERIODIC = "periodic"


class Alarm(TypedDict):
    time: str
    is_enabled: bool
    volume: float
    ring_frequency: RingFrequency


class PriorityLevel(StrEnum):
    "Enum for a RoutineElement's priority level"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RoutineElement(TypedDict):
    priority_level: PriorityLevel
    program: str


class RoutineReward(TypedDict):
    program: str


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
