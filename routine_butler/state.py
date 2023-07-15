from typing import TYPE_CHECKING, Dict, List, Optional, Type

from loguru import logger
from sqlalchemy.engine import Engine

from routine_butler.utils.logging import STATE_CHANGE_LOG_LVL
from routine_butler.utils.misc import (
    Plugin,
    dynamically_get_plugins_from_directory,
)

if TYPE_CHECKING:
    from routine_butler.models import Alarm, Program, Routine, User


class State:
    """Singleton class that holds global state for the app."""

    _engine: Engine = None
    _user: "User" = None
    _plugins: Dict[str, Type[Plugin]] = {}
    _programs: List["Program"] = []
    _next_alarm: Optional["Alarm"] = None
    _next_routine: Optional["Routine"] = None
    _current_routine: Optional["Routine"] = None

    def __new__(cls):
        """Custom __new__ method to make this a singleton class."""
        if not hasattr(cls, "instance"):
            cls.instance = super(State, cls).__new__(cls)
        return cls.instance

    # The following properties are used to access information in private variables that
    # we only want mutated by this class's own methods.

    @property
    def engine(self):
        return self._engine

    @property
    def user(self):
        return self._user

    @property
    def plugins(self):
        return self._plugins

    @property
    def programs(self):
        return self._programs

    @property
    def next_alarm(self):
        return self._next_alarm

    @property
    def next_routine(self):
        return self._next_routine

    @property
    def current_routine(self):
        return self._current_routine

    @property
    def program_titles(self):
        return [p.title for p in self._programs]

    # Set and update methods

    def set_engine(self, engine: Engine):
        """Set the db engine within the global state."""
        self._engine = engine

    def set_current_routine(self, routine: "Routine"):
        """Set the current routine within the global state."""
        self._current_routine = routine

    def set_user(self, user: "User"):
        """Set the current user within the global state."""
        self._user = user
        self.update_next_alarm_and_next_routine()
        self._plugins = dynamically_get_plugins_from_directory()
        self.update_programs()

    def update_programs(self):
        """Pulls from the database and updates the global state's list of programs."""
        self._programs = self._user.get_programs(self.engine)

    def update_next_alarm_and_next_routine(self):
        """Pulls from the database and updates the global state's next alarm and next
        routine."""
        if self._user is not None:
            alarm, routine = self._user.get_next_alarm_and_routine(self.engine)
            self._next_alarm, self._next_routine = alarm, routine
            if self._next_alarm is not None and self._next_routine is not None:
                log_msg = (
                    f"next_alarm=({self._next_alarm.time}, "
                    f"{self._next_alarm.ring_frequency}), "
                    f"next_routine=({self._next_routine.title})"
                )
                logger.log(STATE_CHANGE_LOG_LVL, log_msg)


state = State()  # Instantiate singleton for the rest of the app to use
