from nicegui import ui

from routine_butler.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS
from routine_butler.models.routine import RingFrequency


def ring_frequency_select(value: float) -> ui.select:
    select = ui.select(
        [e.value for e in RingFrequency],
        value=value,
        label="ring frequency",
    )
    return select.props(DFLT_INPUT_PRPS).classes("w-full")
