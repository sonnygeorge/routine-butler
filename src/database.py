"""database module

This module exists to abstract away the details of interacting with the database.

Upon import, this module will:
    - if it does not already exist, create the database file with tables for all
      SQLModel models in the models dir
    - if no user with id == 1, populate the database with a default user for id == 1

Usage:
    from database import database
    from models import User

    # Get a model (and all children) from the database:
    user = database.get(User, 1)

    # Add a model (and all children) to the database:
    database.commit(user)

    # Update a model (and all chilidren) in the database:
    database.commit(user)  # (same as adding)

    # Delete a model (and all children) from the database:
    database.delete(user)
"""


from typing import Any, Callable, List, Type

import sqlalchemy.orm.session
from loguru import logger
from sqlalchemy.orm import joinedload, scoped_session, sessionmaker
from sqlalchemy.orm.exc import DetachedInstanceError
from sqlmodel import SQLModel, create_engine

from models import Routine, Schedule, User

DB_URL = "sqlite:///db.sqlite"
TEST_USER_DEFAULT = User(
    id=1,
    routines=[Routine(id=1, schedules=[Schedule(id=1)])],
)

# Ascertain the necessary database and create engine
engine = create_engine("sqlite:///db.sqlite")
# Create all tables in the database given all models imported
SQLModel.metadata.create_all(engine)

# Redefine Session with SQLAlchemy's scoped_session for it to be thread-local/safe
Session = scoped_session(sessionmaker())
Session.configure(bind=engine, expire_on_commit=False)


class DatabaseWrapper:
    """
    A collection of wrapper functions for interacting with the database.

    This strategies in this wrapper only work if:
     - All models/tables in the DB have a single primary key titled "id"
     - All relationships in the DB are are parent->children/one->zero-or-many
    """

    def _model_row_w_same_id_in_db(self, session, model_object) -> bool:
        """
        Takes a model_object and checks if there is already a row the with the
        same id in the respective table in the DB.
        """
        q = session.query(model_object.__class__.id).filter(
            model_object.__class__.id == model_object.id
        )
        return session.query(q.exists()).scalar()

    def _add_or_merge_to_session_and_commit(
        self, session, model_object
    ) -> None:
        """
        Takes a session and a model object. If the model object has an id that is
        already in the database, the model object is merged into the session. Else,
        the model object is added to the session. The session is then committed.
        """
        is_new = True
        if model_object.id is not None:
            if self._model_row_w_same_id_in_db(session, model_object):
                session.merge(model_object)
                is_new = False
        if is_new:
            session.add(model_object)
        session.commit()

    def _delete_from_session_and_commit(self, session, model_object):
        """
        Takes a session and a model object. If the model object has an id that is
        already in the database, the model object is deleted from the session. The
        session is then committed.
        """
        if self._model_row_w_same_id_in_db(session, model_object):
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

        # After recursing into this model's children, we can now apply the callable
        callable(session, model_object)

    def commit(self, model_object: SQLModel) -> None:
        """
        Adds a new or updates an existing model_object in the database. All children
        of the model are added or updated as well.

        IMPORTANT: This function will NOT delete any children that were removed from
        the model_object. The only way to delete anything from the database is to use
        the delete function. If you commit a model object that has children that have
        been removed, the children will not be deleted, but rather orphaned in the DB
        with a foreign key of NULL.
        """

        with Session() as session:
            self._apply_recursively(
                session, model_object, self._add_or_merge_to_session_and_commit
            )

    def delete(self, model_object: SQLModel) -> None:
        """
        Deletes a model object and all children from the database. Parents are not be
        deleted.

        IMPORTANT: This function is the only way designed for any rows to be deleted
        from the database. If you commit a model object that has children that have
        been removed, the children will not be deleted, but rather orphaned in the DB
        with a foreign key of NULL.
        """

        with Session() as session:
            self._apply_recursively(
                session, model_object, self._delete_from_session_and_commit
            )
            logger.debug(
                f"Deleted {model_object.__class__.__name__} id: {model_object.id} "
                f"and all children from the database."
            )

    def get(self, Model: Type[SQLModel], id: int) -> SQLModel:
        """
        Given an id, eagerly gets a model object with all of its children nested inside.
        """
        with Session() as session:
            model_object = (
                session.query(Model)
                .options(joinedload("*"))
                .filter_by(id=id)
                .first()
            )
        return model_object

    def get_all(self, Model: Type[SQLModel]) -> List[SQLModel]:
        """
        Eagerly gets ALL model objects from a table. For each model object, all of its
        children are retieved as well and nested inside.
        """
        with Session() as session:
            model_objects = session.query(Model).options(joinedload("*")).all()
        return model_objects

    def num_rows_in_table(self, Model: Type[SQLModel]) -> int:
        """Returns the number of rows in a table."""
        with Session() as session:
            count = session.query(Model).count()
        return count


def ascertain_test_user(database: DatabaseWrapper):
    """
    Ascertains the existence of the test user (user_id = 1) in the DB by checking for
    it first, then creating it if it doesn't exist.
    """
    user = database.get(User, id=1)
    if user is None:
        user = TEST_USER_DEFAULT
        database.commit(user)
    logger.debug(
        f"Ascertained the presence of the test user in the DB: {user}"
    )


database = DatabaseWrapper()

ascertain_test_user(database)
