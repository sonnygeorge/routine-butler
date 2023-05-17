from typing import Optional

from nicegui import ui

from routine_butler.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS
from routine_butler.state import state


def plugin_select(value: Optional[str] = None) -> ui.select:
    plugin_select = ui.select(
        [p for p in state.plugins.keys()],
        value=value,
        label="type",
    ).props(DFLT_INPUT_PRPS)
    return plugin_select
