"""
ORM models for the app/database
"""

from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel, JSON, ARRAY, Column

from routine_butler.model.crud_mixin import CRUDMixin
from routine_butler.model.schema import (
    SoundFrequency,
    RoutineElement,
    RoutineReward,
)


PARENT_CHILD_SA_RELATIONSHIP_KWARGS = {
    "cascade": "all, delete, delete-orphan, save-update"
}
CHILD_PARENT_SA_RELATIONSHIP_KWARGS = {"cascade": "save-update, merge"}


class User(SQLModel, CRUDMixin, table=True):
    """SQLModel for "User" objects"""

    username: Optional[str] = Field(default="New User", primary_key=True)

    # Children
    routines: List["Routine"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs=PARENT_CHILD_SA_RELATIONSHIP_KWARGS,
    )
    programs: List["Program"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs=PARENT_CHILD_SA_RELATIONSHIP_KWARGS,
    )


class Program(SQLModel, CRUDMixin, table=True):
    """SQLModel for "Program" objects"""

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    title: Optional[str] = Field(default="New Program")

    # Parent
    user_username: Optional[int] = Field(
        default=None, foreign_key="user.username"
    )
    user: Optional[User] = Relationship(
        back_populates="programs",
        sa_relationship_kwargs=CHILD_PARENT_SA_RELATIONSHIP_KWARGS,
    )


class Routine(SQLModel, CRUDMixin, table=True):
    """SQLModel for "Routine" objects"""

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    title: Optional[str] = Field(default="New Routine")
    target_duration: Optional[int] = Field(default=10)
    target_duration_enabled: bool = Field(default=False)
    elements: List[RoutineElement] = Field(default=[], sa_column=Column(JSON))
    rewards: List[RoutineReward] = Field(default=[], sa_column=Column(JSON))

    # Children
    alarms: List["Alarm"] = Relationship(
        back_populates="routine",
        sa_relationship_kwargs=PARENT_CHILD_SA_RELATIONSHIP_KWARGS,
    )
    # Parent
    user_username: Optional[str] = Field(
        default=None, foreign_key="user.username"
    )
    user: Optional[User] = Relationship(
        back_populates="routines",
        sa_relationship_kwargs=CHILD_PARENT_SA_RELATIONSHIP_KWARGS,
    )


class Alarm(SQLModel, CRUDMixin, table=True):
    """SQLModel for "Alarm" objects"""

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    hour: int = Field(default=0)
    minute: int = Field(default=0)
    enabled: bool = Field(default=False)
    volume: float = Field(default=0.5)
    sound_frequency: SoundFrequency = Field(default=SoundFrequency.CONSTANT)

    # Parent
    routine_id: Optional[int] = Field(default=None, foreign_key="routine.id")
    routine: Optional[Routine] = Relationship(
        back_populates="alarms",
        sa_relationship_kwargs=CHILD_PARENT_SA_RELATIONSHIP_KWARGS,
    )

    def set_time(self, str_time: str):
        """Takes a string in the format "HH:MM" and sets the hour and minute"""
        self.hour, self.minute = str_time.split(":")

    def get_time(self) -> str:
        """Returns a string in the format "HH:MM" from the hour and minute"""
        return f"{self.hour}:{self.minute}"
