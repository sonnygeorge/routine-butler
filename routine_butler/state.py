from typing import TYPE_CHECKING, Dict, List, Optional, Type

from loguru import logger
from sqlalchemy.engine import Engine

from routine_butler.utils.misc import (
    STATE_CHANGE_LOG_LVL,
    Plugin,
    dynamically_get_plugins_from_directory,
)

if TYPE_CHECKING:
    from routine_butler.models import Alarm, Program, Routine, User


class State:
    """Singleton class that holds global state for the app."""

    engine: Engine = None
    user: "User" = None
    plugins: Dict[str, Type[Plugin]] = {}
    programs: List["Program"] = []
    program_titles: List[str] = []
    next_alarm: Optional["Alarm"] = None
    next_routine: Optional["Routine"] = None
    current_routine: Optional["Routine"] = None

    def set_user(self, user: "User"):
        """Set the current user within the global state."""
        self.user = user
        self.update_next_alarm_and_next_routine()
        self.plugins = dynamically_get_plugins_from_directory()
        self.update_programs()

    def update_programs(self):
        """Pulls from the database and updates the global state's list of programs."""
        self.programs = self.user.get_programs(self.engine)
        self.program_titles = [p.title for p in self.programs]

    def update_next_alarm_and_next_routine(self):
        """Pulls from the database and updates the global state's next alarm and next
        routine."""
        if self.user is not None:
            alarm, routine = self.user.get_next_alarm_and_routine(self.engine)
            self.next_alarm, self.next_routine = alarm, routine
            if self.next_alarm is not None and self.next_routine is not None:
                log_msg = (
                    f"next_alarm=({self.next_alarm.time}, "
                    f"{self.next_alarm.ring_frequency}), "
                    f"next_routine=({self.next_routine.title})"
                )
                logger.log(STATE_CHANGE_LOG_LVL, log_msg)


state = State()  # Instantiate singleton for the rest of the app to use
