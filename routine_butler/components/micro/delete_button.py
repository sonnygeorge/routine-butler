from nicegui import ui

from routine_butler.constants import ICON_STRS


def delete_button() -> ui.button:
    return ui.button().props(f"icon={ICON_STRS.delete} color=negative")
