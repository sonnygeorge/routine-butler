from datetime import datetime, timedelta
from typing import List, Optional, Tuple, Union

from pydantic import constr
from sqlalchemy import Column, String
from sqlalchemy.engine import Engine

from routine_butler.models.alarm import Alarm
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

    def get_next_alarm_and_routine(
        self, engine: Engine
    ) -> Tuple[Optional[Alarm], Optional[Routine]]:
        """Queries the database for the user's routines and determines the next upcoming
        alarm/routine.

        Returns:
            A tuple w/ the next alarm and routine or (None, None) if there are no alarms.
        """
        routines = self.get_routines(engine)  # query db for user's routines
        # iterate through alarms in routines to find the next alarm/routine
        now = datetime.now()
        cur_closest_alarm = None
        cur_closest_routine = None
        cur_min_time_until_ring = timedelta(days=1)
        for routine in routines:
            for alarm in routine.alarms:
                # only consider enabled alarms
                if not alarm.is_enabled:
                    continue
                time_until_ring = alarm.get_next_ring_datetime() - now
                print(f"time_until_ring={time_until_ring}")
                # if time until next trigger time
                if time_until_ring < cur_min_time_until_ring:
                    cur_min_time_until_ring = time_until_ring
                    cur_closest_alarm = alarm
                    cur_closest_routine = routine
        return cur_closest_alarm, cur_closest_routine
