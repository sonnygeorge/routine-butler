from typing import Optional

from nicegui import ui

from routine_butler.constants import SDBR
from routine_butler.state import state


def plugin_type_select(value: Optional[str] = None) -> ui.select:
    plugin_select = ui.select(
        [p for p in state.plugin_types.keys()],
        value=value,
        label="type",
    ).props(SDBR.DFLT_INPUT_PRPS)
    return plugin_select
