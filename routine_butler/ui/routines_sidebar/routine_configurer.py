from nicegui import ui
from sqlalchemy.engine import Engine

from routine_butler.models.routine import Routine
from routine_butler.models.user import User
from routine_butler.ui.constants import (
    ABS_ROUTINE_SVG_PATH,
    ICON_STRS,
    ROUTINE_SVG_SIZE,
)
from routine_butler.ui.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS
from routine_butler.ui.constants import SDBR_DFLT_ROW_CLS as DFLT_ROW_CLASSES
from routine_butler.ui.constants import SDBR_V_SPACE as V_SPACE
from routine_butler.ui.primitives.icon_expansion import IconExpansion
from routine_butler.ui.primitives.svg import SVG
from routine_butler.ui.routines_sidebar.alarms_expansion import AlarmsExpansion
from routine_butler.ui.routines_sidebar.elements_expansion import (
    ElementsExpansion,
)


class RoutineConfigurer(IconExpansion):
    def __init__(
        self,
        engine: Engine,
        user: User,
        routine: Routine,
        parent_element: ui.element,
    ):
        self.engine = engine
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
            # top row for setting title
            with ui.row().classes(DFLT_ROW_CLASSES):
                ui.label("Title:")
                # title input
                self.title_input = ui.input(
                    value=routine.title,
                ).props(DFLT_INPUT_PRPS)
                # save button
                title_save_button = ui.button().props(f"icon={ICON_STRS.save}")
                title_save_button.classes("w-1/5")

            # alarms expansion
            with ui.row().classes(DFLT_ROW_CLASSES):
                AlarmsExpansion(engine, routine)

            # routine elements expansion
            with ui.row().classes(DFLT_ROW_CLASSES):
                ElementsExpansion(engine, user, routine)

            # row for target duration input
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE} no-wrap"):
                ui.label("Target Duration:").style("width: 120px;")
                # target duration slider
                target_duration_slider = ui.slider(
                    min=0, max=120, value=routine.target_duration_minutes
                ).classes("w-1/3")
                # target duration label
                target_duration_label = ui.label().style("width: 35px;")
                target_duration_label.bind_text_from(
                    target_duration_slider, "value"
                )
                target_duration_label.set_text(
                    str(routine.target_duration_minutes)
                )
                ui.label("minutes").style("width: 52px;").classes("text-left")
                # target duration enabled toggle
                target_duration_enabled_switch = ui.switch().props("dense")
                target_duration_enabled_switch.value = (
                    routine.target_duration_enabled
                )
            # bottom buttons
            ui.separator()
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                # start routine button
                self.start_button = ui.button().classes("w-3/4")
                self.start_button.props(
                    f"icon={ICON_STRS.play} color=positive"
                )
                # delete routine button
                self.delete_button = ui.button().classes("w-1/5")
                self.delete_button.props(
                    f"icon={ICON_STRS.delete} color=negative"
                )

        # connect handlers to elements
        title_save_button.on(
            "click", lambda: self.handle_title_update(self.title_input.value)
        )
        target_duration_slider.on(
            "change",
            lambda: self.handle_target_duration_update(
                target_duration_slider.value
            ),
        )
        target_duration_enabled_switch.on(
            "click",
            lambda: self.handle_target_duration_enabled_update(
                target_duration_enabled_switch.value
            ),
        )
        self.delete_button.on("click", self.handle_delete)

    def handle_title_update(self, new_title):
        # update the title column in the db
        self.routine.title = new_title
        self.routine.update_self_in_db(self.engine)
        # update the title in the expansion header
        self.header_label.set_text(new_title)

    def handle_target_duration_update(self, new_duration_minutes: int):
        # update the target_duration column in the db
        self.routine.target_duration_minutes = new_duration_minutes
        self.routine.update_self_in_db(self.engine)

    def handle_target_duration_enabled_update(self, value: bool):
        # update the target_duration_enabled column in the db
        self.routine.target_duration_enabled = value
        self.routine.update_self_in_db(self.engine)

    def handle_delete(self):
        # remove the expansion from the parent ui element
        self.parent_element.remove(self.expansion_frame)
        self.parent_element.update()
        # delete the routine from the db
        self.routine.delete_self_from_db(self.engine)
        # delete self from memory
        del self
