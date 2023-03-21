from typing import List, Optional, Type

from sqlmodel import SQLModel, Field, Relationship, Session, create_engine
from sqlalchemy.orm import joinedload, scoped_session, sessionmaker
from sqlalchemy import inspect
from loguru import logger

DB_URL = "sqlite:///db.sqlite"

# Models


class User(SQLModel, table=True):
    """SQLModel for "User" objects"""

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    routines: List["Routine"] = Relationship(back_populates="user")


class Routine(SQLModel, table=True):
    """SQLModel for "Routine" objects"""

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    title: Optional[str] = Field(default="New Routine")

    schedules: List["Schedule"] = Relationship(back_populates="routine")

    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="routines")


class Schedule(SQLModel, table=True):
    """SQLModel for "Schedule" objects"""

    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    hour: int = Field(default=0)
    minute: int = Field(default=0)
    is_active: bool = Field(default=False)

    routine_id: Optional[int] = Field(default=None, foreign_key="routine.id")
    routine: Optional[Routine] = Relationship(back_populates="schedules")


# Ascertain the necessary database and create engine


def ascertain_db():
    """Creates the database with necessary tables if it doesn't exist"""
    engine = create_engine("sqlite:///db.sqlite")
    SQLModel.metadata.create_all(engine)
    logger.debug(f'Ascertained Database with necessary tables at "{DB_URL}"')
    return engine


engine = ascertain_db()

# Database interface

Session = scoped_session(sessionmaker())
Session.configure(bind=engine, expire_on_commit=False)


class Database:
    """Collection of wrapper functions for interacting with the database"""

    def num_rows_in_table(self, Model: Type[SQLModel]):
        with Session() as session:
            count = session.query(Model).count()
        return count

    def _in_db(self, session, model_object) -> bool:
        """
        Checks if a model is already in the database.
        """
        q = session.query(model_object.__class__.id).filter(
            model_object.__class__.id == model_object.id
        )
        return session.query(q.exists()).scalar()

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

    def get_all(self, Model: Type[SQLModel]):
        """
        Gets all models of a given type from the database.

        joinedload("*") is used to eager load all relationships.
        """
        with Session() as session:
            users = session.query(Model).options(joinedload("*")).all()
        return users

    def commit(self, model_object: SQLModel):
        """
        Adds a new or updates an existing model in the database.
        """
        with Session() as session:
            is_new = True
            if model_object.id is not None:
                # Check if id already exists in the database
                if self._in_db(session, model_object):
                    session.merge(model_object)
                    is_new = False
            if is_new:
                session.add(model_object)
            session.commit()
            logger.debug(f"Committed {model_object} to the database.")

    def delete(self, model_object: SQLModel):
        """
        Deletes a model from the database.

        Recursively deletes all children of the model.

        Parents are not be deleted.
        """

        def recursively_delete_children(session, model_object):
            for relationship in model_object.__sqlmodel_relationships__.keys():
                unloaded_properties = inspect(model_object).unloaded
                if relationship not in unloaded_properties:
                    for child in getattr(model_object, relationship):
                        if issubclass(child.__class__, SQLModel):
                            recursively_delete_children(session, child)
                            if self._in_db(session, child):
                                session.delete(child)

        with Session() as session:
            recursively_delete_children(session, model_object)
            session.delete(model_object)
            session.commit()


TEST_USER_DEFAULT = User(
    id=1,
    routines=[Routine(id=1, schedules=[Schedule(id=1)])],
)


def ascertain_test_user(repo: Database):
    """
    Ascertains the existence of the test user (user_id = 1) in the DB by checking for it
    first, then creating it if it doesn't exist.
    """
    user = repo.get(User, id=1)
    if user is None:
        user = TEST_USER_DEFAULT
        repo.commit(user)
    logger.debug(f"Ascertained the presence of the test user in the DB: {user}")


database = Database()

ascertain_test_user(database)
