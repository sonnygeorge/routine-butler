from typing import Any, Optional

from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.orm import joinedload

from routine_butler.database.models import User


class Repository:
    """A singleton object that contains the database engine and provides any
    helpful "repository"-style methods to reduce code duplication."""

    current_username: Optional[str] = None

    def __init__(self):
        self.engine = None

    def create_db(self, url: str):
        self.engine = create_engine(url)
        SQLModel.metadata.create_all(self.engine)

    def session(self):
        """Returns a new session given the engine"""
        return Session(self.engine)

    def eagerly_get_user(
        self, username: str, session: Session
    ) -> Optional[User]:
        """Eagerly loads a user from the database (with all of their subsequent
        data) given a username. Returns None if no such username in DB."""
        return session.get(
            User, username, options=[joinedload("*")], populate_existing=True
        )


## OLD CODE

# """database module

# This module exists to abstract away the details of interacting with the database.

# Upon import, this module will:
#     - if it does not already exist, create the database file with tables for all
#       SQLModel models in the models dir
#     - if no user with id == 1, populate the database with a default user for id == 1

# Usage:
#     from database import database
#     from models import User

#     # Get a model from the database:
#     user = database.get(User, 1)

#     # Add a model to the database:
#     database.commit(user)

#     # Update a model in the database:
#     database.commit(user)  # (same as adding)

#     # Delete a model from the database:
#     database.delete(user)
# """

# import warnings
# from typing import List, Type

# from loguru import logger
# from sqlalchemy.orm import joinedload, scoped_session, sessionmaker
# from sqlmodel import SQLModel, create_engine

# from models import Routine, RoutineProgram, Alarm, User

# # Suppress this warning from deleting a parent after deleting a child
# warnings.filterwarnings(
#     "ignore",
#     message=r".*expected to delete 1 row\(s\); 0 were matched.*",
# )

# DB_URL = "sqlite:///db.sqlite"
# TEST_USER_DEFAULT = User(
#     id=1,
#     routines=[
#         Routine(
#             id=1,
#             alarms=[Alarm(id=1)],
#             routine_programs=[RoutineElement(id=1)],
#         )
#     ],
# )

# # Ascertain the necessary database and create engine
# engine = create_engine("sqlite:///db.sqlite")
# # Create all tables in the database given all models imported
# SQLModel.metadata.create_all(engine)

# # Redefine Session with SQLAlchemy's scoped_session for it to be thread-local/safe
# Session = scoped_session(sessionmaker())
# Session.configure(bind=engine, expire_on_commit=False)


# class DatabaseWrapper:
#     """
#     A collection of wrapper functions for interacting with the database.

#     The strategies in this wrapper are designed to work under the assumptiion that all
#     models/tables in the DB have a single primary key titled "id"
#     """

#     def commit(self, model_object: SQLModel) -> None:
#         """Adds a new or updates an existing model_object in the database"""

#         with Session() as session:
#             session.add(model_object)
#             session.commit()
#             model_object = self.get(model_object.__class__, model_object.id)

#     def delete(self, model_object: SQLModel) -> None:
#         """Deletes a model object from the database"""

#         with Session() as session:
#             session.delete(model_object)
#             session.commit()
#         logger.debug(
#             f"Deleted {model_object.__class__.__name__} id: {model_object.id} "
#             f"and all children from the database."
#         )

#     def get(self, Model: Type[SQLModel], id: int) -> SQLModel:
#         """Given an id, eagerly gets a model object"""
#         with Session() as session:
#             model_object = (
#                 session.query(Model)
#                 .options(joinedload("*"))
#                 .filter_by(id=id)
#                 .first()
#             )
#         return model_object

#     def get_all(self, Model: Type[SQLModel]) -> List[SQLModel]:
#         """Eagerly gets ALL model objects from a table"""
#         with Session() as session:
#             model_objects = session.query(Model).options(joinedload("*")).all()
#         return model_objects

#     def num_rows_in_table(self, Model: Type[SQLModel]) -> int:
#         """Returns the number of rows in a table."""
#         with Session() as session:
#             count = session.query(Model).count()
#         return count


# def ascertain_test_user(database: DatabaseWrapper):
#     """
#     Ascertains the existence of the test user (user_id = 1) in the DB by checking for
#     it first, then creating it if it doesn't exist.
#     """
#     user = database.get(User, id=1)
#     if user is None:
#         user = TEST_USER_DEFAULT
#         database.commit(user)
#     logger.debug(
#         f"Ascertained the presence of the test user in the DB: {user}"
#     )


# database = DatabaseWrapper()

# ascertain_test_user(database)