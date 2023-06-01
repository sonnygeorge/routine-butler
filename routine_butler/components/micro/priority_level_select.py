from nicegui import ui

from routine_butler.models.routine import PriorityLevel


def priority_level_select(value: float) -> ui.select:
    priority_level_select = (
        ui.select(
            [e.value for e in PriorityLevel],
            value=value,
            label="Priority",
        )
        .props("standout dense")
        .classes("w-40")
    )
    return priority_level_select
