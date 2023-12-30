import functools
import importlib
import os
import subprocess
import traceback
from typing import TYPE_CHECKING, Dict, Protocol, Type

from loguru import logger
from nicegui import ui
from pydantic import BaseModel

from routine_butler.globals import (
    CLR_CODES,
    N_SECONDS_BW_HOURLY_TASK_CHECKS,
    N_SECONDS_BW_RING_CHECKS,
    PAGES_WITH_ACTION_PATH_USER_MUST_FOLLOW,
    PLUGINS_DIR_PATH,
    PLUGINS_IMPORT_STR,
    PagePath,
    PlaybackRate,
)
from routine_butler.utils.background_task import BG_TASK_MANAGER

if TYPE_CHECKING:
    from routine_butler.state import State


class Plugin(Protocol):
    """Protocol for plugins within the plugin system of the app"""

    def administer(self, on_complete: callable) -> None:
        ...

    def estimate_duration_in_seconds(self) -> float:
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
        logger.info(f"⏰ Alarm time reached: {state.next_alarm}")
        redirect_to_page(PagePath.RING)


MATHJAX_SCRIPTS = """
<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>
"""


def initialize_page(page: PagePath, state: "State") -> None:
    """Performs a set of standard actions that should be performed at the onset of any
    page load.
    """
    logger.info(f'📱 Initializing page "{page}"... ')
    state.log_state()
    if page == PagePath.DO_ROUTINE:
        ui.add_body_html(MATHJAX_SCRIPTS)

    ui.colors(  # Apply universal color scheme
        primary=CLR_CODES.primary,
        secondary=CLR_CODES.secondary,
        accent=CLR_CODES.accent,
        positive=CLR_CODES.positive,
        negative=CLR_CODES.negative,
        info=CLR_CODES.info,
        warning=CLR_CODES.warning,
    )
    # Make all pages (except login) redirect to login page if user is None
    if page != PagePath.LOGIN and state.user is None:
        redirect_to_page(PagePath.LOGIN)
    # Add header
    if page in PAGES_WITH_ACTION_PATH_USER_MUST_FOLLOW:
        state.build_header(hide_navigation_buttons=True)
    else:
        state.build_header()
        # Monitor for the arrival of the time of the next alarm
        ui.timer(
            N_SECONDS_BW_RING_CHECKS,
            lambda: redirect_to_ring_page_if_next_alarms_time_reached(state),
        )
    # Initiate timer to check for hourly background tasks
    ui.timer(
        N_SECONDS_BW_HOURLY_TASK_CHECKS,
        BG_TASK_MANAGER.check_if_new_hour_and_run_tasks_if_so,
    )


class PendingYoutubeVideo(BaseModel):
    video_id: str
    start_seconds: int = 0
    playback_rate: PlaybackRate = PlaybackRate.PLAYBACK_RATE_NORMAL
    autoplay: bool = False


def log_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Exception occurred in {func.__name__}: {e}\n{traceback.format_exc()}"
            )
            raise

    return wrapper


def open_keyboard():
    logger.info("Opening keyboard...")
    try:
        subprocess.Popen(["matchbox-keyboard", "lq1"])
    except FileNotFoundError:
        pass


def close_keyboard():
    logger.info("Closing keyboard...")
    try:
        subprocess.run(["killall", "matchbox-keyboard"])
    except FileNotFoundError:
        pass
