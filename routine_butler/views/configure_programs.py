from nicegui import ui

from routine_butler.components import micro
from routine_butler.components.header import Header
from routine_butler.components.program_configurer import ProgramConfigurer
from routine_butler.constants import PagePath
from routine_butler.models.program import Program
from routine_butler.state import state
from routine_butler.utils import apply_color_theme, redirect_if_user_is_none

ADD_NEW_PROGRAM_STR = "Add New..."


@ui.page(path=PagePath.SET_PROGRAMS)
def configure_programs():
    def _update_program_select_options():
        program_select.options = state.program_titles + [ADD_NEW_PROGRAM_STR]
        program_select.value = ""
        program_select.update()

    def hdl_select_program_to_configure(program_title: Program):
        program_configurer_frame.clear()
        if program_title == ADD_NEW_PROGRAM_STR:
            program = Program()
        else:
            idx = state.program_titles.index(program_title)
            program = state.programs[idx]

        with program_configurer_frame:
            p_conf = ProgramConfigurer(program)

        p_conf.save_button.on("click", _update_program_select_options)
        p_conf.save_button.on("click", program_configurer_frame.clear)

    def hdl_delete_program(program_title: Program):
        idx = state.program_titles.index(program_title)
        program = state.programs[idx]
        program.delete_self_from_db(state.engine)  # remove from db
        state.programs.pop(idx)  # remove from state
        state.program_titles.pop(idx)
        _update_program_select_options()

    redirect_if_user_is_none(state.user)
    apply_color_theme()
    Header()

    with ui.row().classes(
        "absolute-center w-10/12 flex flex-col content-center"
    ):
        with micro.card().classes(
            "flex flex-row items-center justify-center mb-4"
        ).style("width: 853px"):
            micro.program_svg(size=20, color="lightgray").classes("mx-1")
            program_select = micro.program_select(
                state.program_titles + [ADD_NEW_PROGRAM_STR]
            )
            ui.separator().props("vertical").classes("mx-3")
            configure_button = ui.button("Configure").classes("grow")
            delete_button = micro.delete_button().classes("w-20")

        program_configurer_frame = ui.element("div")

    configure_button.on(
        "click",
        lambda: hdl_select_program_to_configure(program_select.value),
    )
    delete_button.on(
        "click",
        lambda: hdl_delete_program(program_select.value),
    )
