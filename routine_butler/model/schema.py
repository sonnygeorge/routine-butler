from enum import Enum
from typing import TypedDict

from pydantic.dataclasses import dataclass


class PriorityLevel(str, Enum):
    "Enum for a RoutineElement's priority level"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class SoundFrequency(str, Enum):
    "Enum for a Alarm's sound frequency"
    CONSTANT = "constant"
    PERIODIC = "periodic"


class RoutineElement(TypedDict):
    priority_level: PriorityLevel
    program: str


class RoutineReward(TypedDict):
    program: str
