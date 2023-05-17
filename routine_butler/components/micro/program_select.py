from typing import List, Optional, Union

from nicegui import ui

from routine_butler.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS
from routine_butler.models.program import Program


def program_select(
    program_titles: Union[List[Program], List[str]],
    value: Optional[str] = None,
) -> ui.select:
    options = [
        p.title if isinstance(p, Program) else p for p in program_titles
    ]
    program_select = ui.select(
        options=options,
        value=value,
        label="program",
    ).props(DFLT_INPUT_PRPS)
    return program_select.classes("w-full")
