import datetime
from typing import TYPE_CHECKING, Dict, List, Optional, Type

from loguru import logger
from nicegui import ui
from sqlalchemy.engine import Engine

from routine_butler.components.header import Header
from routine_butler.utils.logging import STATE_LOG_LVL
from routine_butler.utils.misc import (
    PendingYoutubeVideo,
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
    _is_dark_mode: bool = False
    _is_pending_orated_entry: bool = False
    _pending_youtube_video: Optional[PendingYoutubeVideo] = None
    _n_programs_traversed: int = 0
    _element_programs_queue: Optional[List["Program"]] = None
    _pending_run_data_to_be_added_to_db: Optional[dict] = None
    _current_program_start_time: Optional[datetime.datetime] = None

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

    def __init__(self):
        ui.timer(0.2, self._check_header_and_update_is_dark_mode)

    def _check_header_and_update_is_dark_mode(self):
        if self._header is not None:
            self._is_dark_mode = self._header._is_dark_mode

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
    def header(self):
        return self._header

    @property
    def program_titles(self):
        return [p.title for p in self._programs]

    @property
    def is_pending_orated_entry(self):
        return self._is_pending_orated_entry

    @property
    def pending_youtube_video(self):
        return self._pending_youtube_video

    @property
    def n_programs_traversed(self):
        return self._n_programs_traversed

    @property
    def element_programs_queue(self):
        return self._element_programs_queue

    @property
    def pending_run_data_to_be_added_to_db(self):
        return self._pending_run_data_to_be_added_to_db

    @property
    def current_program_start_time(self):
        return self._current_program_start_time

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
        self._header = Header(
            hide_navigation_buttons, is_dark_mode=self._is_dark_mode
        )
        self.update_header()

    def set_is_pending_orated_entry(self, is_pending_orated_entry: bool):
        self._is_pending_orated_entry = is_pending_orated_entry

    def set_pending_youtube_video(self, video_id: str):
        self._pending_youtube_video = video_id

    def set_n_programs_traversed(self, n: int):
        self._n_programs_traversed = n

    def set_element_programs_queue(self, queue: List["Program"]):
        self._element_programs_queue = queue

    def set_pending_run_data_to_be_added_to_db(self, run_data: dict):
        self._pending_run_data_to_be_added_to_db = run_data

    def set_current_program_start_time(self, dt: datetime.datetime):
        self._current_program_start_time = dt


state = State()  # Instantiate singleton for the rest of the app to use
