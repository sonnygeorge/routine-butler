from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel

PARENT_CHILD_SA_RELATIONSHIP_KWARGS = {
    "cascade": "all, delete, delete-orphan, save-update"
}


class User(SQLModel, table=True):
    """SQLModel for "User" objects"""

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    routines: List["Routine"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs=PARENT_CHILD_SA_RELATIONSHIP_KWARGS,
    )


class Routine(SQLModel, table=True):
    """SQLModel for "Routine" objects"""

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    title: Optional[str] = Field(default="New Routine")

    schedules: List["Schedule"] = Relationship(
        back_populates="routine",
        sa_relationship_kwargs=PARENT_CHILD_SA_RELATIONSHIP_KWARGS,
    )
    user: Optional[User] = Relationship(back_populates="routines")


class Schedule(SQLModel, table=True):
    """SQLModel for "Schedule" objects"""

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    hour: int = Field(default=0)
    minute: int = Field(default=0)
    is_active: bool = Field(default=False)

    routine_id: Optional[int] = Field(default=None, foreign_key="routine.id")
    routine: Optional[Routine] = Relationship(back_populates="schedules")
