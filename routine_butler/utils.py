import importlib
import os
from typing import TYPE_CHECKING, Dict, Optional, Protocol, Tuple, Type

from loguru import logger
from nicegui import ui
from sqlalchemy.engine import Engine

from routine_butler.components.header import Header
from routine_butler.configs import (
    CLR_CODES,
    N_SECONDS_BETWEEN_ALARM_CHECKS,
    PLUGINS_DIR_PATH,
    PagePath,
)

if TYPE_CHECKING:
    from routine_butler.models import Alarm, Routine, User
    from routine_butler.state import State


IMPORT_STR_FOR_PLUGINS = "routine_butler.plugins.{module}"

SECONDS_IN_DAY = 24 * 60 * 60

PAGES_WITH_IMPERATIVE_ACTION_PATH_FOR_USER_TO_FOLLOW = [
    PagePath.DO_ROUTINE,
    PagePath.RING,
    PagePath.LOGIN,
]

DATABASE_LOG_LVL = "DB EVENT"
HARDWARE_LOG_LVL = "HW EVENT"
STATE_CHANGE_LOG_LVL = "STT CHNG"

logger.level(DATABASE_LOG_LVL, no=33, color="<magenta>")
logger.level(HARDWARE_LOG_LVL, no=34, color="<yellow>")
logger.level(STATE_CHANGE_LOG_LVL, no=34, color="<blue>")


def get_next_alarm_and_routine_from_db(
    user: "User", engine: Engine
) -> Tuple[Optional["Alarm"], Optional["Routine"]]:
    # query db for user's routines
    routines = user.get_routines(engine)
    # iterate through alarms in routines to find the next alarm/routine
    next_alarm = None
    next_routine = None
    min_seconds_until_alarm = SECONDS_IN_DAY  # no alarm is more than day away
    for routine in routines:
        for alarm in routine.alarms:
            # only consider enabled alarms
            if not alarm.is_enabled:
                continue
            # get seconds until alarm
            cur_seconds_until_alarm = alarm.get_seconds_until_time()
            # if past, add a day's worth of seconds to negative amount
            if cur_seconds_until_alarm <= 0:
                cur_seconds_until_alarm += SECONDS_IN_DAY
            # if less than current min, update min
            if cur_seconds_until_alarm < min_seconds_until_alarm:
                min_seconds_until_alarm = cur_seconds_until_alarm
                next_alarm = alarm
                next_routine = routine
    return next_alarm, next_routine


class Plugin(Protocol):
    """Protocol for plugins within the plugin system of the app"""

    def administer(self, on_complete: callable):
        ...

    def dict(self) -> dict:
        ...


def snake_to_upper_camel(snake_case_str: str) -> str:
    return "".join(word.capitalize() for word in snake_case_str.split("_"))


def dynamically_get_plugins_from_directory() -> Dict[str, Type[Plugin]]:
    """Dynamically loads all program types from the programs directory"""
    program_types = {}
    for file_name in os.listdir(PLUGINS_DIR_PATH):
        if not file_name.startswith("_") and file_name.endswith(".py"):
            module_name = file_name[:-3]
            import_str = IMPORT_STR_FOR_PLUGINS.format(module=module_name)
            module = importlib.import_module(import_str)
            class_name = snake_to_upper_camel(module_name)
            program_types[class_name] = getattr(module, class_name)
    return program_types


def redirect_to_page(
    page_path: PagePath, n_seconds_before_redirect: float = 0.1
):
    def _redirect_to_page():
        logger.info(f"Redirecting to page: {page_path}")
        ui.open(page_path)

    ui.timer(n_seconds_before_redirect, _redirect_to_page, once=True)


def redirect_to_ring_page_if_next_alarms_time_reached(state: "State") -> None:
    if state.next_alarm is not None and state.next_alarm.should_ring():
        redirect_to_page(PagePath.RING)


def initialize_page(page: PagePath, state: "State"):
    # apply universal color scheme
    ui.colors(
        primary=CLR_CODES.primary,
        secondary=CLR_CODES.secondary,
        accent=CLR_CODES.accent,
        positive=CLR_CODES.positive,
        negative=CLR_CODES.negative,
        info=CLR_CODES.info,
        warning=CLR_CODES.warning,
    )
    # make all pages (except login) redirect to login page if user is None
    if page != PagePath.LOGIN and state.user is None:
        redirect_to_page(PagePath.LOGIN)
    # add header
    if page in PAGES_WITH_IMPERATIVE_ACTION_PATH_FOR_USER_TO_FOLLOW:
        Header(hide_navigation_buttons=True)
    else:
        Header()
        # monitor for the arrival of the time of the next alarm
        ui.timer(
            N_SECONDS_BETWEEN_ALARM_CHECKS,
            lambda: redirect_to_ring_page_if_next_alarms_time_reached(state),
        )


def move_up_in_list(list_: list, idx_to_move: int):
    list_.insert(idx_to_move - 1, list_.pop(idx_to_move))


def move_down_in_list(list_: list, idx_to_move: int):
    list_.insert(idx_to_move + 1, list_.pop(idx_to_move))
