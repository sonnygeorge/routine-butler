from typing import TYPE_CHECKING, Dict, List, Optional, Type

from loguru import logger
from sqlalchemy.engine import Engine

from routine_butler.utils import (
    STATE_CHANGE_LOG_LVL,
    Plugin,
    dynamically_get_plugins_from_directory,
)

if TYPE_CHECKING:
    from routine_butler.models import Alarm, Program, Routine, User


NEXT_ALARM_UPDATE_STR = (
    "next_alarm=({time}, {ring_frequency}), next_routine=({routine_title})"
)


class State:
    engine: Engine = None
    user: "User" = None
    programs: List["Program"] = []
    program_titles: List[str] = []
    plugin_types: Dict[str, Type[Plugin]] = {}
    current_routine: Optional["Routine"] = None
    next_alarm: Optional["Alarm"] = None
    next_routine: Optional["Routine"] = None

    def update_next_alarm_and_next_routine(self):
        if self.user is not None:
            alarm, routine = self.user.get_next_alarm_and_routine(self.engine)
            self.next_alarm, self.next_routine = alarm, routine
            if self.next_routine is not None:
                log_msg = NEXT_ALARM_UPDATE_STR.format(
                    time=self.next_alarm.time,
                    ring_frequency=self.next_alarm.ring_frequency,
                    routine_title=self.next_routine.title,
                )
                logger.log(STATE_CHANGE_LOG_LVL, log_msg)

    def set_user(self, user: "User"):
        self.user = user
        self.update_next_alarm_and_next_routine()
        self.plugin_types = dynamically_get_plugins_from_directory()
        self.update_programs()

    def update_programs(self):
        self.programs = [p for p in self.user.get_programs(self.engine)]
        self.program_titles = [p.title for p in self.programs]


state = State()  # instantiate singleton for the rest of the app to import
