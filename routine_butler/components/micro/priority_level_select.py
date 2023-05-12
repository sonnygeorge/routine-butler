from nicegui import ui

from routine_butler.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS
from routine_butler.models.routine import PriorityLevel


def priority_level_select(value: float) -> ui.select:
    priority_level_select = ui.select(
        [e.value for e in PriorityLevel],
        value=value,
        label="priority",
    ).props(DFLT_INPUT_PRPS)
    return priority_level_select.classes("w-full")
