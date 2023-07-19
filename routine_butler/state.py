from typing import TYPE_CHECKING, Dict, List, Optional, Type

from loguru import logger
from sqlalchemy.engine import Engine

from routine_butler.components.header import Header
from routine_butler.utils.logging import STATE_LOG_LVL
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
    _header: Optional[Header] = None

    def __new__(cls):
        """Custom __new__ method to make this a singleton class."""
        if not hasattr(cls, "instance"):
            cls.instance = super(State, cls).__new__(cls)
        return cls.instance

    def __str__(self):
        """Custom __str__ method for logging."""
        return (
            f"✨ next_alarm={self.next_alarm} ✨ next_routine="
            f"{self.next_routine.title if self.next_routine else None} "
            "✨ current_routine="
            f"{self.current_routine.title if self.current_routine else None}"
        )

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
        logger.log(STATE_LOG_LVL, f"🔄 {self}")

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
            logger.log(STATE_LOG_LVL, f"🔄 {self}")
            self.update_header()

    def update_header(self):
        if self._header is None:
            return
        if self._next_alarm is not None:
            time_str = self._next_alarm.time_str
        else:
            time_str = None
        self._header.next_alarm_display.update(time_str)

    def log_state(self):
        """Log the current state of the app."""
        logger.log(STATE_LOG_LVL, f"ℹ️  {self}")

    def build_header(self, hide_navigation_buttons: bool = False):
        self._header = Header(hide_navigation_buttons)
        self.update_header()


state = State()  # Instantiate singleton for the rest of the app to use
