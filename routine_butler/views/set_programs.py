from typing import Optional

from nicegui import ui

from routine_butler.components import micro
from routine_butler.components.header import Header
from routine_butler.components.program_configurer import ProgramConfigurer
from routine_butler.constants import PagePath
from routine_butler.models.program import Program
from routine_butler.state import state
from routine_butler.utils import apply_color_theme, redirect_if_user_is_none

ADD_NEW_PROGRAM_STR = "Add new program"


@ui.page(path=PagePath.SET_PROGRAMS)
def set_programs():
    def update_program_select_options():
        program_select.options = state.program_titles + [ADD_NEW_PROGRAM_STR]
        program_select.update()

    def hdl_select_program(program_title: Optional[Program] = None):
        program_configurer_frame.clear()
        if program_title == ADD_NEW_PROGRAM_STR:
            program = Program()
        else:
            idx = state.program_titles.index(program_title)
            program = state.programs[idx]

        with program_configurer_frame:
            p_conf = ProgramConfigurer(program)

        p_conf.save_button.on("click", update_program_select_options)
        p_conf.save_button.on("click", program_configurer_frame.clear)

    redirect_if_user_is_none(state.user)
    apply_color_theme()
    Header()

    with ui.row():
        with ui.card():
            program_select = micro.program_select(state.program_titles)
            configure_button = ui.button("Configure")
        program_configurer_frame = ui.element("div")

    configure_button.on(
        "click",
        lambda: hdl_select_program(program_select.value),
    )
