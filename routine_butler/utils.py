import importlib
import os
from typing import TYPE_CHECKING, Dict, Protocol, Type

from loguru import logger
from nicegui import ui

from routine_butler.components.header import Header
from routine_butler.configs import (
    CLR_CODES,
    N_SECONDS_BETWEEN_ALARM_CHECKS,
    PAGES_WITH_ACTION_PATH_USER_MUST_FOLLOW,
    PLUGINS_DIR_PATH,
    PLUGINS_IMPORT_STR,
    PagePath,
)

if TYPE_CHECKING:
    from routine_butler.state import State


DATABASE_LOG_LVL = "DB EVENT"
HARDWARE_LOG_LVL = "HW EVENT"
STATE_CHANGE_LOG_LVL = "STT CHNG"

logger.level(DATABASE_LOG_LVL, no=33, color="<magenta>")
logger.level(HARDWARE_LOG_LVL, no=34, color="<yellow>")
logger.level(STATE_CHANGE_LOG_LVL, no=34, color="<blue>")


class Plugin(Protocol):
    """Protocol for plugins within the plugin system of the app"""

    def administer(self, on_complete: callable) -> None:
        ...

    def dict(self) -> dict:
        ...


def move_up_in_list(list_: list, idx_to_move: int) -> None:
    """Moves an item in a list up by one index."""
    list_.insert(idx_to_move - 1, list_.pop(idx_to_move))


def move_down_in_list(list_: list, idx_to_move: int) -> None:
    """Moves an item in a list down by one index."""
    list_.insert(idx_to_move + 1, list_.pop(idx_to_move))


def snake_to_upper_camel_case(snake_case_str: str) -> str:
    """Converts a snake_case string to UpperCamelCase."""
    return snake_case_str.title().replace("_", "")


def dynamically_get_plugins_from_directory() -> Dict[str, Type[Plugin]]:
    """
    Dynamically loads all plugin from the plugins directory.

    Returns:
        A dictionary mapping plugin names to their corresponding plugins.
    """
    plugins = {}
    for file_name in os.listdir(PLUGINS_DIR_PATH):
        if not file_name.startswith("_") and file_name.endswith(".py"):
            module_name = file_name[:-3]
            import_str = PLUGINS_IMPORT_STR.format(module=module_name)
            module = importlib.import_module(import_str)
            class_name = snake_to_upper_camel_case(module_name)
            plugins[class_name] = getattr(module, class_name)
    return plugins


def redirect_to_page(
    page_path: PagePath, n_seconds_before_redirect: float = 0.1
) -> None:
    """Invokes a NiceGUI timer to redirect to a given page after a given delay."""

    def _redirect_to_page():
        logger.info(f"Redirecting to page: {page_path}")
        ui.open(page_path)

    ui.timer(n_seconds_before_redirect, _redirect_to_page, once=True)


def redirect_to_ring_page_if_next_alarms_time_reached(state: "State") -> None:
    """Redirects to the ring page if the time of the next alarm has been reached."""
    if state.next_alarm is not None and state.next_alarm.should_ring():
        redirect_to_page(PagePath.RING)


def initialize_page(page: PagePath, state: "State") -> None:
    """Performs a set of standard actions that should be performed at the onset of any
    page load.
    """
    ui.colors(  # apply universal color scheme
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
    if page in PAGES_WITH_ACTION_PATH_USER_MUST_FOLLOW:
        Header(hide_navigation_buttons=True)
    else:
        Header()
        # monitor for the arrival of the time of the next alarm
        ui.timer(
            N_SECONDS_BETWEEN_ALARM_CHECKS,
            lambda: redirect_to_ring_page_if_next_alarms_time_reached(state),
        )
