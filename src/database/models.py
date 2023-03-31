"""
ORM models for the database.
"""

# from enum import Enum
# from typing import List, Optional

# from sqlmodel import Field, Relationship, SQLModel

# PARENT_CHILD_SA_RELATIONSHIP_KWARGS = {
#     "cascade": "all, delete, delete-orphan, save-update"
# }
# CHILD_PARENT_SA_RELATIONSHIP_KWARGS = {"cascade": "save-update, merge"}


# class PriorityLevel(str, Enum):
#     LOW = "low"
#     MEDIUM = "medium"
#     HIGH = "high"


# class User(SQLModel, table=True):
#     """SQLModel for "User" objects"""

#     id: Optional[int] = Field(default=None, primary_key=True, nullable=False)

#     # Children
#     routines: List["Routine"] = Relationship(
#         back_populates="user",
#         sa_relationship_kwargs=PARENT_CHILD_SA_RELATIONSHIP_KWARGS,
#     )

#     programs: List["Program"] = Relationship(
#         back_populates="user",
#         sa_relationship_kwargs=PARENT_CHILD_SA_RELATIONSHIP_KWARGS,
#     )


# class Routine(SQLModel, table=True):
#     """SQLModel for "Routine" objects"""

#     id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
#     title: Optional[str] = Field(default="New Routine")

#     # Children
#     schedules: List["Schedule"] = Relationship(
#         back_populates="routine",
#         sa_relationship_kwargs=PARENT_CHILD_SA_RELATIONSHIP_KWARGS,
#     )
#     routine_elements: List["RoutineElement"] = Relationship(
#         back_populates="routine",
#         sa_relationship_kwargs=PARENT_CHILD_SA_RELATIONSHIP_KWARGS,
#     )
#     # Parent
#     user_id: Optional[int] = Field(default=None, foreign_key="user.id")
#     user: Optional[User] = Relationship(
#         back_populates="routines",
#         sa_relationship_kwargs=CHILD_PARENT_SA_RELATIONSHIP_KWARGS,
#     )


# class Schedule(SQLModel, table=True):
#     """SQLModel for "Schedule" objects"""

#     id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
#     hour: int = Field(default=0)
#     minute: int = Field(default=0)
#     is_on: bool = Field(default=False)

#     # Parent
#     routine_id: Optional[int] = Field(default=None, foreign_key="routine.id")
#     routine: Optional[Routine] = Relationship(
#         back_populates="schedules",
#         sa_relationship_kwargs=CHILD_PARENT_SA_RELATIONSHIP_KWARGS,
#     )


# class RoutineElement(SQLModel, table=True):
#     """
#     SQLModel that extends a "Program" to contain the necessary information to be
#     used in a "Routine"
#     """

#     __tablename__ = "routine_element"

#     id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
#     order_index: int = Field(default=0)
#     priority_level: PriorityLevel = Field(default=PriorityLevel.MEDIUM)

#     # Parents
#     routine_id: Optional[int] = Field(default=None, foreign_key="routine.id")
#     routine: Optional[Routine] = Relationship(
#         back_populates="routine_elements",
#         sa_relationship_kwargs=CHILD_PARENT_SA_RELATIONSHIP_KWARGS,
#     )

#     program_id: Optional[int] = Field(default=None, foreign_key="program.id")
#     program: Optional["Program"] = Relationship(
#         back_populates="routine_elements",
#         sa_relationship_kwargs=CHILD_PARENT_SA_RELATIONSHIP_KWARGS,
#     )


# class Program(SQLModel, table=True):
#     """SQLModel for "Program" objects"""

#     id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
#     title: Optional[str] = Field(default="New Program")

#     # Children
#     routine_elements: List[RoutineElement] = Relationship(
#         back_populates="program",
#         sa_relationship_kwargs=PARENT_CHILD_SA_RELATIONSHIP_KWARGS,
#     )

#     # Parent
#     user_id: Optional[int] = Field(default=None, foreign_key="user.id")
#     user: Optional[User] = Relationship(
#         back_populates="programs",
#         sa_relationship_kwargs=CHILD_PARENT_SA_RELATIONSHIP_KWARGS,
#     )