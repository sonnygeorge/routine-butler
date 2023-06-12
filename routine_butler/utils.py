import importlib
import os
import subprocess
from typing import TYPE_CHECKING, Dict, Protocol, Type

from loguru import logger
from nicegui import ui

from routine_butler.constants import ABS_PLUGINS_DIR_PATH, CLR_CODES, PagePath

if TYPE_CHECKING:
    from routine_butler.models.user import User


def apply_color_theme():
    ui.colors(
        primary=CLR_CODES.primary,
        secondary=CLR_CODES.secondary,
        accent=CLR_CODES.accent,
        positive=CLR_CODES.positive,
        negative=CLR_CODES.negative,
        info=CLR_CODES.info,
        warning=CLR_CODES.warning,
    )


def redirect_to_page(
    page_path: PagePath, n_seconds_before_redirect: float = 0.1
):
    def _redirect_to_page():
        ui.open(page_path)

    ui.timer(n_seconds_before_redirect, _redirect_to_page, once=True)


def redirect_if_user_is_none(user: "User"):
    if user is None:
        redirect_to_page(PagePath.LOGIN)


def move_up_in_list(list_: list, idx_to_move: int):
    list_.insert(idx_to_move - 1, list_.pop(idx_to_move))


def move_down_in_list(list_: list, idx_to_move: int):
    list_.insert(idx_to_move + 1, list_.pop(idx_to_move))


def snake_to_upper_camel(snake_case_str: str) -> str:
    return "".join(word.capitalize() for word in snake_case_str.split("_"))


class ProgramPlugin(Protocol):
    """Protocol for program types to implement"""

    def administer(self, on_complete: callable):
        ...

    def dict(self) -> dict:
        ...


def dynamically_get_plugins() -> Dict[str, Type[ProgramPlugin]]:
    """Dynamically loads all program types from the programs directory"""
    program_types = {}
    for file_name in os.listdir(ABS_PLUGINS_DIR_PATH):
        if not file_name.startswith("_") and file_name.endswith(".py"):
            module_name = file_name[:-3]
            module = importlib.import_module(
                f"routine_butler.plugins.{module_name}"
            )
            class_name = snake_to_upper_camel(module_name)
            program_types[class_name] = getattr(module, class_name)
    return program_types


# define and add custom log level for database events
DB_LOG_LVL = "DB EVENT"
logger.level(DB_LOG_LVL, no=33, color="<magenta>")

# define and add custom log level for hardware events
HW_LOG_LVL = "HW EVENT"
logger.level(HW_LOG_LVL, no=34, color="<yellow>")


def open_keyboard():
    print("OPENING KEYBOARD")
    subprocess.Popen(["matchbox-keyboard"])


def close_keyboard():
    print("CLOSING KEYBOARD")
    subprocess.run(["killall", "matchbox-keyboard"])
