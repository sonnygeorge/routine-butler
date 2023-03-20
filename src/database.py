from typing import List, Optional, Type

from sqlmodel import SQLModel, Field, Relationship, Session, create_engine
from sqlalchemy.orm import joinedload, scoped_session, sessionmaker
from loguru import logger

DB_URL = "sqlite:///db.sqlite"

# Models


class UserModel(SQLModel, table=True):
    """SQLModel for "User" objects"""

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    routines: List["RoutineModel"] = Relationship(back_populates="user")


class RoutineModel(SQLModel, table=True):
    """SQLModel for "Routine" objects"""

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    title: Optional[str] = Field(default="New Routine")

    schedules: List["ScheduleModel"] = Relationship(back_populates="routine")

    user_id: Optional[int] = Field(default=None, foreign_key="usermodel.id")
    user: Optional[UserModel] = Relationship(back_populates="routines")


class ScheduleModel(SQLModel, table=True):
    """SQLModel for "Schedule" objects"""

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    hour: int = Field(default=0)
    minute: int = Field(default=0)
    is_active: bool = Field(default=False)

    routine_id: Optional[int] = Field(default=None, foreign_key="routinemodel.id")
    routine: Optional[RoutineModel] = Relationship(back_populates="schedules")


# Ascertain the necessary database and create engine


def ascertain_db():
    """Creates the database if it doesn't exist"""
    engine = create_engine("sqlite:///db.sqlite")
    SQLModel.metadata.create_all(engine)
    logger.debug(f'Ascertained Database with necessary tables at "{DB_URL}"')
    return engine


engine = ascertain_db()

# Database interface

Session = scoped_session(sessionmaker())
Session.configure(bind=engine)


class Database:
    def get(self, Model: Type[SQLModel], id: int):
        """
        Gets a model from the database given its id.

        joinedload("*") is used to eager load all relationships.
        """
        with Session() as session:
            user = (
                session.query(Model).options(joinedload("*")).filter_by(id=id).first()
            )
        return user

    def update(self, model_object: SQLModel):
        """
        Adds a new or updates an existing model in the database.
        """
        with Session() as session:
            session.merge(model_object)
            session.commit()


TEST_USER_DEFAULT = UserModel(
    id=1, routines=[RoutineModel(id=1, schedules=[ScheduleModel(id=1)])]
)


def ascertain_test_user(repo: Database):
    """
    Ascertains the existence of the test user (user_id = 1) in the DB by checking for it
    first, then creating it if it doesn't exist.
    """
    user = repo.get(UserModel, id=1)
    if user is None:
        user = TEST_USER_DEFAULT
        repo.update(user)
    logger.debug(f"Ascertained the presence of the test user in the DB: {user}")


database = Database()

ascertain_test_user(database)
