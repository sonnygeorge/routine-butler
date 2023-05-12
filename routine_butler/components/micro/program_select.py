from typing import List

from nicegui import ui

from routine_butler.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS
from routine_butler.models.program import Program


def program_select(choosable_programs: List[Program]) -> ui.select:
    program_select = ui.select(
        [p.title for p in choosable_programs],
        value="",
        label="program",
    ).props(DFLT_INPUT_PRPS)
    return program_select.classes("w-full")
