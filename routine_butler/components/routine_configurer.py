from nicegui import ui

from routine_butler.components import micro
from routine_butler.components.alarms_expansion import AlarmsExpansion
from routine_butler.components.elements_expansion import ElementsExpansion
from routine_butler.components.primitives import SVG, IconExpansion
from routine_butler.constants import (
    ABS_ROUTINE_SVG_PATH,
    ROUTINE_SVG_SIZE,
    PagePath,
)
from routine_butler.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS
from routine_butler.constants import SDBR_DFLT_ROW_CLS as DFLT_ROW_CLASSES
from routine_butler.constants import SDBR_V_SPACE as V_SPACE
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
            "size": ROUTINE_SVG_SIZE,
            "color": "black",
        }
        super().__init__(routine.title, icon=SVG, icon_kwargs=svg_kwargs)
        self.expansion_frame.classes(f"mt-{V_SPACE}")

        with self:
            with ui.row().classes(DFLT_ROW_CLASSES):
                ui.label("Title:")
                self.title_input = ui.input(
                    value=routine.title,
                ).props(DFLT_INPUT_PRPS)
                title_save_button = micro.save_button().classes("w-1/5")
            with ui.row().classes(DFLT_ROW_CLASSES):
                AlarmsExpansion(routine)
            with ui.row().classes(DFLT_ROW_CLASSES):
                ElementsExpansion(routine)
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE} no-wrap"):
                target_duration_slider = micro.target_duration_slider(
                    routine.target_duration_minutes
                )
                target_duration_enabled_switch = ui.switch(
                    value=routine.target_duration_enabled
                ).props("dense")
            ui.separator()
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                start_button = micro.play_button().classes("w-3/4")
                delete_button = micro.delete_button().classes("w-1/5")

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
        self.parent_element.remove(self.expansion_frame)
        self.parent_element.update()
        self.routine.delete_self_from_db(state.engine)
        del self
