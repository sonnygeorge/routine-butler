from typing import Optional

from nicegui import ui

from routine_butler.state import state


def plugin_type_select(value: Optional[str] = None) -> ui.select:
    plugin_select = ui.select(
        [p for p in state.plugin_types.keys()],
        value=value,
        label="type",
    ).props("standout dense")
    return plugin_select
