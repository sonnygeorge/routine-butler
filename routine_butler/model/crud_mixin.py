from typing import Any, Self

from pydantic import BaseModel
from loguru import logger
from sqlalchemy.orm import joinedload, make_transient
from sqlalchemy import inspect
from sqlmodel import SQLModel, Session


LOG_LVL = "DATABASE"
logger.level(LOG_LVL, no=33, color="<yellow>")


def ensure_loaded_relationships(instance: SQLModel, session: Session):
    """Loads all relationships for an instance"""
    if instance not in session:
        session.add(instance)
    for unloaded in inspect(instance).unloaded:
        getattr(instance, unloaded)
        if isinstance(unloaded, list) and all(
            isinstance(x, SQLModel) for x in unloaded
        ):
            for item in unloaded:
                ensure_loaded_relationships(item)
        elif isinstance(unloaded, SQLModel):
            ensure_loaded_relationships(unloaded)


class CRUDMixin(BaseModel):
    """Class to add CRUD methods to SQLModel classes/instances"""

    @classmethod
    def get_from_db(cls, session: Session, uid: Any) -> Self:
        """Gets an instance of the class AND its relationships from the session given its uid"""
        instance = session.get(
            cls, ident=uid, options=[joinedload("*")], populate_existing=True
        )
        logger.log(LOG_LVL, f"Getting {cls.__name__} with uid '{uid}' from db")
        return instance

    def add_to_db(self, session: Session) -> SQLModel:
        """Commits an instance to the db"""
        logger.log(LOG_LVL, f"Creating {self.__class__.__name__} in db")
        if self not in session:
            session.add(self)
        else:
            session.merge(self)
        session.commit()
        ensure_loaded_relationships(self, session)
        return self

    def update_in_db(self, session: Session, **kwargs) -> SQLModel:
        """Updates instance with the given kwargs"""
        if self not in session:
            session.add(self)
        else:
            session.merge(self)
        for key, value in kwargs.items():
            setattr(self, key, value)
        session.commit()
        ensure_loaded_relationships(self, session)
        return self

    def delete_from_db(self, session: Session) -> None:
        """Deletes instance from the database"""
        logger.log(
            LOG_LVL, f"Deleting {self.__class__.__name__} instance from db"
        )
        session.delete(self)
        session.commit()
        make_transient(self)