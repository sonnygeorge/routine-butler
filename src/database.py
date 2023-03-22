from typing import List, Optional, Type, Callable, Any

from sqlmodel import SQLModel, Field, Relationship, Session, create_engine
from sqlalchemy.orm import joinedload, scoped_session, sessionmaker
import sqlalchemy.orm.session
from sqlalchemy.orm.exc import DetachedInstanceError
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


# TODO: Document better and consider design


class DatabaseWrapper:
    """
    A collection of wrapper functions for interacting with the database.

    This strategies in this wrapper only work if:
     - All models/tables in the DB have a single primary key titled "id"
     - All relationships in the DB are are parent->children/one->zero-or-many
    """

    def _in_db(self, session, model_object) -> bool:
        """
        Checks if a model is already in the database.
        """
        q = session.query(model_object.__class__.id).filter(
            model_object.__class__.id == model_object.id
        )
        return session.query(q.exists()).scalar()

    def _add_or_merge(self, session, model_object):
        is_new = True
        if model_object.id is not None:
            # Check if id already exists in the database
            if self._in_db(session, model_object):
                session.merge(model_object)
                is_new = False
        if is_new:
            session.add(model_object)
        session.commit()

    def _delete(self, session, model_object):
        if self._in_db(session, model_object):
            session.delete(model_object)
            session.commit()

    def _apply_recursively(
        self,
        session: sqlalchemy.orm.session.Session,
        model_object: SQLModel,
        callable: Callable[[sqlalchemy.orm.session.Session, SQLModel], Any],
    ) -> None:
        """
        Applies the callable to the model_object and all children recursively.

        Applies the callable beginning with the innermost children and works back up
        to the original model_object.

        args:
            session: the SQLAlchemy session to use
            model_object: the SQLModel model object to apply the callable to
            callable: The callable to apply--must have a signature of:
                Callable[[sqlalchemy.orm.session.Session, SQLModel], Any]

        returns:
            None
        """
        for relationship in model_object.__sqlmodel_relationships__.keys():
            # Skip relationships that aren't attached to the session
            try:
                getattr(model_object, relationship)
            except DetachedInstanceError:
                continue

            def is_children(model_object, relationship):
                # Since the DB only has parent->children/one->many relationships,
                # we can assume that if a relationship comes back as a list, it
                # is children.
                return isinstance(getattr(model_object, relationship), list)

            if is_children(model_object, relationship):
                # Manually set empty children relationships to empty lists, since
                # they otherwise, don't seem to be "eager loaded" and persisted
                # outside of session context.
                if getattr(model_object, relationship) == []:
                    setattr(model_object, relationship, [])
                    continue  # no need to proceed, no children to recurse into

                # Finally, for each child, we can recurse
                for child in getattr(model_object, relationship):
                    self._apply_recursively(session, child, callable)

        # After resurcing into this model's children, we can now apply the callable
        callable(session, model_object)

    def commit(self, model_object: SQLModel):
        """
        Adds a new or updates an existing model in the database.
        """

        with Session() as session:
            self._apply_recursively(session, model_object, self._add_or_merge)
            logger.debug(f"Committed {model_object} and all children to the database.")

    def delete(self, model_object: SQLModel):
        """
        Deletes a model object and all children from the database. Parents are not be deleted.
        """

        with Session() as session:
            self._apply_recursively(session, model_object, self._delete)
            logger.debug(f"Deleted {model_object} and all children from the database.")

    def get(self, Model: Type[SQLModel], id: int):
        """
        Eagerly gets a model and all child relationships from the database given an id.
        """
        with Session() as session:
            user = (
                session.query(Model).options(joinedload("*")).filter_by(id=id).first()
            )
        return user

    def get_all(self, Model: Type[SQLModel]) -> List[SQLModel]:
        """
        Eagerly gets all model objects (with their nested child relationships) from a table.
        """
        with Session() as session:
            users = session.query(Model).options(joinedload("*")).all()
        return users

    def num_rows_in_table(self, Model: Type[SQLModel]) -> int:
        """Returns the number of rows in a table."""
        with Session() as session:
            count = session.query(Model).count()
        return count


TEST_USER_DEFAULT = User(
    id=1,
    routines=[Routine(id=1, schedules=[Schedule(id=1)])],
)


def ascertain_test_user(repo: DatabaseWrapper):
    """
    Ascertains the existence of the test user (user_id = 1) in the DB by checking for it
    first, then creating it if it doesn't exist.
    """
    user = repo.get(User, id=1)
    if user is None:
        user = TEST_USER_DEFAULT
        repo.commit(user)
    logger.debug(f"Ascertained the presence of the test user in the DB: {user}")


database = DatabaseWrapper()

ascertain_test_user(database)
