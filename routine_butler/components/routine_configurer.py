from nicegui import ui

from routine_butler.components import micro
from routine_butler.components.alarms_expansion import AlarmsExpansion
from routine_butler.components.chronology_expansion import ChronologyExpansion
from routine_butler.components.primitives import SVG, IconExpansion
from routine_butler.constants import ABS_ROUTINE_SVG_PATH, PagePath
from routine_butler.models.routine import Routine
from routine_butler.state import state
from routine_butler.utils import redirect_to_page


class RoutineConfigurer(IconExpansion):
    def __init__(
        self,
        routine: Routine,
        parent_element: ui.element,
    ):
        self.routine = routine
        self.parent_element = parent_element
        svg_kwargs = {
            "fpath": ABS_ROUTINE_SVG_PATH,
            "size": 28,
            "color": "black",
        }
        super().__init__(
            routine.title, icon=SVG, icon_kwargs=svg_kwargs, width="965px"
        )

        with self:
            top_row = ui.row().classes("items-center justify-center")
            with top_row.classes("pt-4 gap-x-7 w-full"):
                with ui.row().classes("items-center"):
                    ui.label("Title:")
                    self.title_input = micro.input(
                        value=routine.title,
                    ).props("standout dense")
                    title_save_button = micro.save_button().classes("w-20")

                ui.separator().props("vertical")

                objs = micro.target_duration_slider(
                    routine.target_duration_minutes,
                    routine.target_duration_enabled,
                )
                target_duration_slider, target_duration_enabled_switch = objs

                AlarmsExpansion(routine)
                ChronologyExpansion(routine)

                ui.separator().classes("bg-gray-100")
                bottom_row = ui.row().style("width: 850px")
                with bottom_row.classes("items-center justify-end mb-5"):
                    start_button = micro.play_button().classes("grow")
                    ui.separator().props("vertical").classes("mx-3")
                    delete_button = micro.delete_button().style("width: 155px")

        title_save_button.on(
            "click", lambda: self.hdl_title_update(self.title_input.value)
        )
        target_duration_slider.on(
            "change",
            lambda: self.hdl_target_duration_update(
                target_duration_slider.value
            ),
        )
        target_duration_enabled_switch.on(
            "click",
            lambda: self.hdl_target_duration_enabled_update(
                target_duration_enabled_switch.value
            ),
        )
        start_button.on("click", self.hdl_start)
        delete_button.on("click", self.hdl_delete)

    def hdl_title_update(self, new_title):
        self.routine.title = new_title
        self.routine.update_self_in_db(state.engine)
        self.header_label.set_text(new_title)

    def hdl_target_duration_update(self, new_duration_minutes: int):
        self.routine.target_duration_minutes = new_duration_minutes
        self.routine.update_self_in_db(state.engine)

    def hdl_target_duration_enabled_update(self, value: bool):
        self.routine.target_duration_enabled = value
        self.routine.update_self_in_db(state.engine)

    def hdl_start(self):
        state.pending_routine_to_run = self.routine
        redirect_to_page(PagePath.DO_ROUTINE)

    def hdl_delete(self):
        self.parent_element.remove(self.bordered_frame)
        self.parent_element.update()
        self.routine.delete_self_from_db(state.engine)
        state.update_next_alarm()
        del self
