"""This module is an implementation of a strategy to interact with a database using
SQLAlchemy ORM models and Pydantic models.

The basic idea of the strategy is to bake the methods for a model's interactions with the
database into the Pydantic model itself, making them database-"batteries-included".

Usage:
    1. Define a SQLAlchemy ORM model that inherits from this module's BaseDBORMModel:

        class HeroORM(BaseDBORMModel):
            __tablename__ = "heroes"

            name = Column(String(60))

    2. Define a Pydantic model that inherits from this module's BaseDBPydanticModel and
    specify an association to an ORM model in its Config:

        class Hero(BaseDBPydanticModel):
            name: constr(max_length=60)

            class Config:
                orm_model = HeroORM

    3. Use the inherited methods to perform interactions with the database:

        hero = Hero(name="Superman")
        hero.add_to_db(engine)
        hero.name = "Batman"
        hero.update_in_db(engine)
        hero.delete_from_db(engine)
"""

import datetime
import sys
import warnings
from typing import List, Optional, Protocol, Self, Union

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.engine.base import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.sql.elements import BinaryExpression, UnaryExpression

from routine_butler.utils import DB_LOG_LVL


def log_db_event(
    class_name: str,
    method_name: str,
    uid: Optional[Union[str, int]] = None,
) -> None:
    """Logs a database event.

    Args:
        class_name (str): The name of the BaseDBPydanticModel class that the event is
            associated with.
        method_name (str): The name of the method that the event is associated with.
        uid (Optional[Union[str, int]], optional): The uid (if applicable) of the
            instance that the event is associated with. Defaults to None.
    """
    if uid is not None:
        str_to_be_logged = f"{class_name}(uid:{uid}) - {method_name}()"
    else:
        str_to_be_logged = f"{class_name} - {method_name}()"
    logger.log(DB_LOG_LVL, str_to_be_logged)


class AttemptedSetOnReadOnlyFieldError(Exception):
    """Raised when a protected field is attempted to be set by external code."""


class InstanceAlreadyExistsError(Exception):
    """Raised when a model is added to the database twice."""


class DatabaseUpdateFailedError(Exception):
    """Raised when an attempted BaseDBPydanticModel.update_in_db() fails."""


class DatabaseDeletionFailedError(Exception):
    """Raised when an attempted BaseDBPydanticModel.delete_from_db() fails."""


class DeclarativeBaseProxyType:
    """
    Proxy type for monkey-patching a type-hint to the return value of declarative_base().
    """

    class metadata(Protocol):
        def create_all(self, engine: Engine) -> None:
            ...

        def drop_all(self, engine: Engine) -> None:
            ...


SQLAlchemyBase: DeclarativeBaseProxyType = declarative_base()

now = datetime.datetime.utcnow


class BaseDBORMModel(SQLAlchemyBase):
    """Base for SQLAlchemy ORM models that interact with a database.

    Bakes in:
        1. a uid field (auto-incrementing primary key)
        2. a created_at field
        3. an updated_at field
    """

    __abstract__ = True

    uid = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now)


class BaseDBPydanticModel(BaseModel):
    """
    Base for Pydantic models that interact with a database via SQLAlchemy ORM models.

    Bakes in:
        1. a uid field
        2. a created_at field
        3. an updated_at field

    ...which reflect the respective fields of BaseDBORMModel.

    Suitable for realtively simple applications that do not need to multitask many
    different database interactions per session.
    """

    uid: Optional[int] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None

    _READ_ONLY_FIELDS = {"uid", "created_at", "updated_at"}

    def __init__(self, **kwargs):
        self._validate_orm_model()
        # if any protected fields are being initialized, raise error
        if any(field in kwargs.keys() for field in self._READ_ONLY_FIELDS):
            raise AttemptedSetOnReadOnlyFieldError(
                f"Cannot initialize the following fields: {self._READ_ONLY_FIELDS}"
            )
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        """Prevents external modification of a protected field."""
        if name in self._READ_ONLY_FIELDS:
            # determine if the scope that is attempting to modify the attribute is
            # within a class
            outer_scope_locals = sys._getframe(1).f_locals
            if "cls" in outer_scope_locals.keys():
                modifying_class = outer_scope_locals["cls"]
            elif "self" in outer_scope_locals.keys():
                modifying_class = outer_scope_locals["self"].__class__
            else:
                modifying_class = None
            # if not within a class of if the modifying class is not self.__class__,
            # raise error
            if modifying_class != self.__class__:
                raise AttemptedSetOnReadOnlyFieldError(
                    f"Cannot modify field: '{name}'"
                )
        super().__setattr__(name, value)

    class Config:
        """Pydantic model config--see: docs.pydantic.dev/usage/model_config/"""

        # This provides the Pydantic model with a from_orm() method that converts
        # the SQLAlchemy ORM model instance to a Pydantic model instance--see:
        # docs.pydantic.dev/usage/models/#orm-mode-aka-arbitrary-class-instances
        orm_mode: bool = True
        # We store SQLAlchemy ORM model that represents the corresponding database
        # table here. Otherwise, Pydantic would consider it a data field.
        orm_model: BaseDBORMModel = None

    def _to_orm(self) -> BaseDBORMModel:
        """Converts self into a SQLAlchemy ORM model instance."""
        return self.Config.orm_model(**self.dict())

    @classmethod
    def _validate_orm_model(cls):
        """Validates that the Config.orm_model exists and is of type DBORMModel."""
        if cls.Config.orm_model is None:
            raise NotImplementedError(
                f"Class {cls.__name__} must have a orm_model attribute in its Config"
            )
        if not issubclass(cls.Config.orm_model, BaseDBORMModel):
            raise TypeError(
                f"Class {cls.__name__}.Config.orm_model must be a subclass of DBORMModel"
            )

    @classmethod
    def query_one(
        cls, engine: Engine, filter_: Optional[BinaryExpression] = None
    ) -> Optional[Self]:
        """Queries the database for a single instance of the model.

        Args:
            engine (Engine): The SQLAlchemy engine to use for the query.
            filter_ (Optional[BinaryExpression]): The SQLAlchemy binary expression that
                will be used to filter the query. Defaults to None.
        Returns:
            Optional[Self]: The first result of the query, or None if no results.
        """
        cls._validate_orm_model()
        results = cls.query(engine, filter_=filter_, limit=2)
        if len(results) > 1:
            warnings.warn(
                "query_one() called with a `filter_` argument that returned multiple "
                "results from the database. Returning the first result."
            )
        return results[0] if results else None

    @classmethod
    def query(
        cls,
        engine: Engine,
        filter_: Optional[BinaryExpression] = None,
        order_by: Optional[UnaryExpression] = None,
        limit: int = 10_000,
    ) -> List[Self]:
        """Queries the database for multiple instances of the model.

        Args:
            engine (Engine): The SQLAlchemy engine to use for the query.
            filter_ (Optional[BinaryExpression]): The SQLAlchemy binary expression that
                will be used to filter the query. Defaults to None.
            order_by (Optional[UnaryExpression]): The SQLAlchemy unary expression that
                will be used to order the query. Defaults to None.
            limit (int): The maximum number of results to return. Defaults to 10,000.
        Returns:
            List[Self]: The results of the query, or an empty list if no results.
        """
        log_db_event(cls.__name__, "query")
        cls._validate_orm_model()
        if order_by is None:
            order_by = cls.Config.orm_model.created_at.asc()
        with Session(engine) as session:
            query = session.query(cls.Config.orm_model)
            if filter_ is not None:
                query = query.filter(filter_)
            results = query.order_by(order_by).limit(limit).all()
            return [cls.from_orm(obj) for obj in results] if results else []

    def add_self_to_db(self, engine: Engine) -> None:
        """Adds the model instance to the database.

        Args:
            engine (Engine): The SQLAlchemy engine to use for the query.
        Returns:
            None
        """
        log_db_event(self.__class__.__name__, "add_self_to_db", self.uid)
        self._validate_orm_model()
        with Session(engine) as session:
            orm_model_instance = self._to_orm()
            session.add(orm_model_instance)
            try:
                session.commit()
            except IntegrityError as e:
                raise InstanceAlreadyExistsError(
                    "Model instance already in database"
                ) from e
            self.uid = orm_model_instance.uid
            self.created_at = orm_model_instance.created_at
            self.updated_at = orm_model_instance.updated_at

    def update_self_in_db(self, engine: Engine) -> None:
        """Updates the model instance in the database

        Args:
            engine (Engine): The SQLAlchemy engine to use for the query.
        Returns:
            None
        """
        log_db_event(self.__class__.__name__, "update_self_in_db", self.uid)
        self._validate_orm_model()
        updates_to_make = self.dict()
        updates_to_make["updated_at"] = now()
        with Session(engine) as session:
            rows_affected = (
                session.query(self.Config.orm_model)
                .filter(self.Config.orm_model.uid == self.uid)
                .update(updates_to_make)
            )
            if rows_affected == 0:
                raise DatabaseUpdateFailedError(
                    "Expected to update 1 row, but 0 were set to be updated -- Are "
                    "you sure the model instance was already added to the database?"
                )
            if rows_affected > 1:
                raise DatabaseUpdateFailedError(
                    f"Expected to update 1 row, but {rows_affected} were set to be"
                    f"updated - Pending update was NOT committed to the database"
                )
            session.commit()
        self.updated_at = updates_to_make["updated_at"]

    def delete_self_from_db(self, engine: Engine) -> None:
        """Deletes the model instance from the database

        Args:
            engine (Engine): The SQLAlchemy engine to use for the query.
        Returns:
            None
        """
        log_db_event(self.__class__.__name__, "delete_self_from_db", self.uid)
        self._validate_orm_model()
        with Session(engine) as session:
            rows_affected = (
                session.query(self.Config.orm_model)
                .filter(self.Config.orm_model.uid == self.uid)
                .delete()
            )
            if rows_affected == 0:
                raise DatabaseDeletionFailedError(
                    "Expected to delete 1 row, but 0 were set to be deleted -- Are "
                    "you sure the model instance was already added to the database?"
                )
            if rows_affected > 1:
                raise DatabaseDeletionFailedError(
                    f"Expected to delete 1 row, but {rows_affected} were set to be"
                    f"deleted - Pending deletion was NOT committed to the database"
                )
            session.commit()
        self.uid = None
        self.created_at = None
        self.updated_at = None
