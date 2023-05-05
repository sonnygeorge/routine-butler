from typing import List, Union

from pydantic import constr
from sqlalchemy import Column, String
from sqlalchemy.engine import Engine

from routine_butler.models.base import (
    BaseDBORMModel,
    BaseDBPydanticModel,
    InstanceAlreadyExistsError,
)
from routine_butler.models.program import Program
from routine_butler.models.routine import Routine


class UserORM(BaseDBORMModel):
    """BaseDBORMModel model for a User"""

    __tablename__ = "users"

    USERNAME_LENGTH_LIMIT = 60

    username = Column(String(USERNAME_LENGTH_LIMIT), unique=True)


class User(BaseDBPydanticModel):
    """BaseDBPydanticModel model for a User"""

    username: constr(max_length=UserORM.USERNAME_LENGTH_LIMIT)

    class Config:
        orm_model = UserORM

    def _add_child(
        self, engine: Engine, child: Union[Routine, Program]
    ) -> None:
        """Sets the child's user_uid to this user's uid and adds it to or updates it in
        the database
        """
        child.user_uid = self.uid
        try:
            child.add_self_to_db(engine)
        except InstanceAlreadyExistsError:
            child.update_self_in_db(engine)

    def _get_children(
        self,
        engine: Engine,
        child_type: Union[type[Routine], type[Program]],
    ) -> Union[List[Routine], List[Program]]:
        """Queries the database for all children of the given type"""
        is_child_filter_expr = child_type.Config.orm_model.user_uid == self.uid
        return child_type.query(engine, filter_=is_child_filter_expr)

    def add_routine(self, engine: Engine, routine: Routine) -> None:
        """Adds the given routine to the database"""
        self._add_child(engine, routine)

    def add_program(self, engine: Engine, program: Program) -> None:
        """Adds the given program to the database"""
        self._add_child(engine, program)

    def get_routines(self, engine: Engine) -> List[Routine]:
        """Queries the database for all routines belonging to this user"""
        return self._get_children(engine, Routine)

    def get_programs(self, engine: Engine) -> List[Program]:
        """Queries the database for all programs belonging to this user"""
        return self._get_children(engine, Program)
