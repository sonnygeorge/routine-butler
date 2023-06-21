from typing import TYPE_CHECKING, List, Optional

from nicegui import ui

if TYPE_CHECKING:
    from routine_butler.models import PriorityLevel, RingFrequency


def plugin_type_select(
    value: Optional[str], plugin_types: List[str]
) -> ui.select:
    plugin_select = ui.select(
        [p for p in plugin_types],
        value=value,
        label="Type",
    )
    return plugin_select.props("standout dense")


def program_select(
    value: Optional[str],
    program_titles: List[str],
) -> ui.select:
    program_select = ui.select(
        options=program_titles,
        value=value,
        label="Program",
    )
    return program_select.props("standout dense").classes("w-64")


def priority_level_select(
    value: float, priority_levels: List["PriorityLevel"]
) -> ui.select:
    priority_level_select = ui.select(
        [e.value for e in priority_levels],
        value=value,
        label="Priority",
    )
    return priority_level_select.props("standout dense").classes("w-40")


def ring_frequency_select(
    value: float, ring_frequencies: List["RingFrequency"]
) -> ui.select:
    select = ui.select(
        [e.value for e in ring_frequencies],
        value=value,
        label="Ring Frequency",
    )
    return select.props("standout dense")
