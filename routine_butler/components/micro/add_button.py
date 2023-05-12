from nicegui import ui

from routine_butler.constants import ICON_STRS


def add_button() -> ui.button:
    return ui.button().props(f"icon={ICON_STRS.add}")
