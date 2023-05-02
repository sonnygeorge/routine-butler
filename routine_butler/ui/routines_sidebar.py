import os
from typing import Union

from loguru import logger
from nicegui import ui
from sqlalchemy.engine import Engine

from routine_butler.models.routine import (
    Alarm,
    PriorityLevel,
    Routine,
    RoutineElement,
    RoutineReward,
    SoundFrequency,
)
from routine_butler.models.user import User
from routine_butler.ui.constants import (
    ICON_STRS,
    PROGRAM_SVG_SIZE,
    REWARD_SVG_SIZE,
    ROUTINE_SVG_SIZE,
)
from routine_butler.ui.constants import RTNS_SDBR_WIDTH as DRAWER_WIDTH
from routine_butler.ui.constants import SDBR_BREAKPOINT as BREAKPOINT
from routine_butler.ui.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS
from routine_butler.ui.constants import SDBR_DFLT_ROW_CLS as DFLT_ROW_CLASSES
from routine_butler.ui.constants import SDBR_V_SPACE as V_SPACE
from routine_butler.ui.primitives.sidebar_expansion import SidebarExpansion
from routine_butler.ui.primitives.svg import SVG

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTINE_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/routine-icon.svg")
PROGRAM_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/program-icon.svg")
REWARD_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/reward-icon.svg")


class AlarmsExpansion(SidebarExpansion):
    def __init__(self, engine: Engine, routine: Routine):
        self.engine = engine
        self.routine = routine
        super().__init__("Alarms", icon=ICON_STRS.alarm)

        with self:
            # alarms frame
            self.alarms_frame = ui.element("div")
            self._update_alarms_frame()

            # add alarm button
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                self.add_alarm_button = ui.button().props(
                    f"icon={ICON_STRS.add}"
                )
                self.add_alarm_button.classes("w-full")
                self.add_alarm_button.on("click", self.handle_add_alarm)

    @property
    def num_alarms(self) -> int:
        return len(self.routine.alarms)

    def _update_alarms_frame(self):
        self.alarms_frame.clear()
        with self.alarms_frame:
            for idx, alarm in enumerate(self.routine.alarms):
                self._add_ui_row(row_idx=idx, alarm=alarm)

    def _add_ui_row(self, row_idx: int, alarm: Alarm):
        with ui.row().classes(DFLT_ROW_CLASSES + " gap-x-0"):
            # time input
            with ui.element("div").style("width: 23%;"):
                time_input = ui.input(value=alarm["time"])
                time_input.props(DFLT_INPUT_PRPS).classes("w-full")
                with time_input as input:
                    with input.add_slot("append"):
                        icon = ui.icon("access_time").classes("cursor-pointer")
                        icon.on("click", lambda: menu.open())
                        with ui.menu() as menu:
                            time_setter = ui.time()
                            time_setter.bind_value(time_input)
                            time_setter.on(
                                "update:model-value",
                                lambda: self.handle_time_change(
                                    row_idx, time_input.value
                                ),
                            )  # FIXME: add throttle
            # volume knob
            with ui.element("div").style("width: 10%;").classes("mx-1"):
                vol_knob = ui.knob(value=alarm["volume"], track_color="grey-2")
                vol_knob.props("size=lg thickness=0.3")
                with vol_knob:
                    ui.icon("volume_up").props("size=xs")
                vol_knob.on(
                    "change",
                    lambda: self.handle_change_volume(row_idx, vol_knob.value),
                )
            # sound frequency select
            with ui.element("div").style("width: 32%;"):
                sound_frequency_select = ui.select(
                    [e.value for e in SoundFrequency],
                    value=alarm["sound_frequency"],
                    label="ring frequency",
                ).props(DFLT_INPUT_PRPS)
                sound_frequency_select.classes("w-full")
                sound_frequency_select.on(
                    "update:model-value",
                    lambda: self.handle_select_sound_frequency(
                        row_idx, sound_frequency_select.value
                    ),
                )
            # toggle switch
            with ui.element("div").style("width: 34px;").classes("mx-1"):
                switch = ui.switch().props("dense")
                switch.value = alarm["enabled"]
                switch.on(
                    "click",
                    lambda: self.handle_toggle_enabled(row_idx, switch.value),
                )
            # delete button
            self.delete_button = ui.button()
            self.delete_button.props(
                f"icon={ICON_STRS.delete} color=negative dense"
            )
            self.delete_button.on(
                "click", lambda: self.handle_delete_alarm(row_idx)
            )

    def handle_add_alarm(self):
        alarm = {
            "time": "12:00",
            "volume": 0.5,
            "sound_frequency": SoundFrequency.CONSTANT,
            "enabled": True,
        }
        self.routine.alarms.append(alarm)
        self.routine.update_self_in_db(self.engine)
        with self.alarms_frame:
            self._add_ui_row(row_idx=self.num_alarms - 1, alarm=alarm)

    def handle_time_change(self, row_idx: int, new_time: str):
        self.routine.alarms[row_idx]["time"] = new_time
        self.routine.update_self_in_db(self.engine)

    def handle_change_volume(self, row_idx: int, new_volume: float):
        self.routine.alarms[row_idx]["volume"] = new_volume
        self.routine.update_self_in_db(self.engine)

    def handle_select_sound_frequency(
        self, row_idx: int, new_frequency: SoundFrequency
    ):
        self.routine.alarms[row_idx]["sound_frequency"] = new_frequency
        self.routine.update_self_in_db(self.engine)

    def handle_toggle_enabled(self, row_idx: int, value: bool):
        self.routine.alarms[row_idx]["enabled"] = value
        self.routine.update_self_in_db(self.engine)

    def handle_delete_alarm(self, row_idx: int):
        self.routine.alarms.pop(row_idx)
        self.routine.update_self_in_db(self.engine)
        self._update_alarms_frame()


class ElementsExpansion(SidebarExpansion):
    def __init__(self, engine: Engine, user: User, routine: Routine):
        self.engine = engine
        self.user = user
        self.routine = routine

        svg_kwargs = {
            "fpath": PROGRAM_SVG_FPATH,
            "size": PROGRAM_SVG_SIZE,
            "color": "black",
        }

        super().__init__("Chronology", icon=SVG, icon_kwargs=svg_kwargs)
        self.classes("justify-between items-center")

        with self:
            self.rows_frame = ui.element("div")
            self._update_rows_frame()

            # bottom buttons
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                # add routine element button
                self.add_routine_element_button = ui.button().props(
                    f"icon={ICON_STRS.add}"
                )
                self.add_routine_element_button.classes("w-3/4")
                self.add_routine_element_button.on(
                    "click", self.handle_add_element
                )
                # add reward buttom
                self.add_reward_element_button = ui.button().classes(
                    "items-center w-1/5 bg-secondary"
                )
                with self.add_reward_element_button:
                    SVG(REWARD_SVG_FPATH, size=REWARD_SVG_SIZE, color="white")
                self.add_reward_element_button.on(
                    "click",
                    self.handle_add_reward,
                )

    @property
    def num_elements(self):
        return len(self.routine.elements)

    def _update_rows_frame(self):
        """Clear and repopulates the 'div'/frame containing `RoutineElementRow`s
        in order to accomplish internal reording"""
        # remove any rows currently in the frame
        self.rows_frame.clear()
        # instantiate new rows within the frame
        with self.rows_frame:
            for idx, element in enumerate(self.routine.elements):
                self._add_ui_row(row_idx=idx, row_data=element)
            for idx, reward in enumerate(self.routine.rewards):
                self._add_ui_row(
                    row_idx=self.num_elements + idx, row_data=reward
                )

    def _add_ui_row(
        self, row_idx: int, row_data: Union[RoutineElement, RoutineReward]
    ):
        accent_color = (
            "primary" if "priority_level" in row_data.keys() else "secondary"
        )  # FIXME

        with ui.row().classes(DFLT_ROW_CLASSES + " gap-x-0"):
            # number
            number = ui.element("div").style("width: 5%;")
            number.classes("mx-0 self-start w-full")
            number.classes(f"rounded bg-{accent_color} w-full drop-shadow")
            with number:
                lbl = ui.label(f"{row_idx + 1}.")
                lbl.style("height: 1.125rem;")
                lbl.classes("text-white text-center text-xs text-bold")
                lbl.classes("flex items-center justify-center")
            # program select
            with ui.element("div").style("width: 32%;"):
                program_select = ui.select(
                    [
                        p.title for p in self.user.get_programs(self.engine)
                    ],  # FIXME
                    value="",
                    label="program",
                ).props(DFLT_INPUT_PRPS)
                program_select.classes("w-full")
                program_select.on(
                    "update:model-value",
                    lambda: self.handle_select_program(
                        row_idx=row_idx, new_program=program_select.value
                    ),
                )
            # priority level select
            with ui.element("div").style("width: 27%;"):
                if "priority_level" in row_data.keys():
                    priority_level_select = ui.select(
                        [e.value for e in PriorityLevel],
                        value=row_data["priority_level"],
                        label="priority",
                    ).props(DFLT_INPUT_PRPS)
                    priority_level_select.classes("w-full")
                    priority_level_select.on(
                        "update:model-value",
                        lambda: self.handle_select_priority(
                            row_idx=row_idx,
                            new_priority=priority_level_select.value,
                        ),
                    )
                else:
                    q_item = ui.element("q-item").props("dense")
                    q_item.style("height: 2.5rem;")
                    cls = "items-center justify-center border-secondary"
                    cls += " rounded w-full border-dotted border-2"
                    q_item.classes(cls)
                    with q_item:
                        SVG(
                            REWARD_SVG_FPATH,
                            size=REWARD_SVG_SIZE,
                            color="#e5e5e5",
                        )
            # order movement buttons
            order_buttons_frame = ui.row().classes("gap-x-1 justify-center")
            with order_buttons_frame.style("width: 18%;"):
                up_button = ui.button().classes(f"bg-{accent_color}")
                up_button.props(f"icon={ICON_STRS.up_arrow} dense")
                up_button.on(
                    "click",
                    lambda: self.handle_move_row_up(row_idx=row_idx),
                )
                down_button = ui.button().classes(f"bg-{accent_color}")
                down_button.props(f"icon={ICON_STRS.down_arrow} dense")
                down_button.on(
                    "click",
                    lambda: self.handle_move_row_down(row_idx=row_idx),
                )
            # delete button
            with ui.element("div").style("width: 7%;"):
                delete_button = ui.button()
                delete_button.props(
                    f"icon={ICON_STRS.delete} color=negative dense"
                )
                delete_button.on(
                    "click",
                    lambda: self.handle_delete_row(row_idx=row_idx),
                )

    def handle_add_element(self):
        element = {"priority_level": PriorityLevel.MEDIUM, "program": ""}
        self.routine.elements.append(element)
        self.routine.update_self_in_db(self.engine)

        if len(self.routine.rewards) == 0:
            new_row_idx = len(self.routine.elements + self.routine.rewards) - 1
            with self.rows_frame:
                self._add_ui_row(row_idx=new_row_idx, row_data=element)
        else:
            self._update_rows_frame()

    def handle_add_reward(self):
        reward = {"program": ""}
        self.routine.rewards.append(reward)
        self.routine.update_self_in_db(self.engine)

        new_row_idx = len(self.routine.elements + self.routine.rewards) - 1
        with self.rows_frame:
            self._add_ui_row(row_idx=new_row_idx, row_data=reward)

    def handle_move_row_up(self, row_idx: int):
        if row_idx == self.num_elements or row_idx == 0:
            logger.debug("Cannot move upward")
            return
        elif row_idx > self.num_elements:  # if reward
            # swap reward at index with reward at index - 1
            row_idx = row_idx - self.num_elements
            self.routine.rewards.insert(
                row_idx - 1, self.routine.rewards.pop(row_idx)
            )
        else:  # elif element
            # swap element at index with element at index - 1
            self.routine.elements.insert(
                row_idx - 1, self.routine.elements.pop(row_idx)
            )
        self.routine.update_self_in_db(self.engine)
        self._update_rows_frame()

    def handle_move_row_down(self, row_idx: int):
        if (
            row_idx == self.num_elements - 1
            or row_idx == len(self.routine.elements + self.routine.rewards) - 1
        ):
            logger.debug("Cannot move downward")
            return
        elif row_idx >= self.num_elements:  # if reward
            # swap reward at index with reward at index + 1
            row_idx = row_idx - self.num_elements
            self.routine.rewards.insert(
                row_idx + 1, self.routine.rewards.pop(row_idx)
            )
        else:  # elif element
            # swap element at index with element at index + 1
            self.routine.elements.insert(
                row_idx + 1, self.routine.elements.pop(row_idx)
            )
        self.routine.update_self_in_db(self.engine)
        self._update_rows_frame()

    def handle_delete_row(self, row_idx: int):
        if row_idx >= self.num_elements:  # if reward
            # delete reward at index
            self.routine.rewards.pop(row_idx - self.num_elements)
        else:  # elif element
            # delete element at index
            self.routine.elements.pop(row_idx)
        self.routine.update_self_in_db(self.engine)
        self._update_rows_frame()

    def handle_select_program(self, row_idx: int, new_program: str):
        if row_idx >= self.num_elements:  # if reward
            # update program in reward at index
            self.routine.rewards[row_idx - self.num_elements][
                "program"
            ] = new_program
        else:  # elif element
            # update program in element at index
            self.routine.elements[row_idx]["program"] = new_program
        self.routine.update_self_in_db(self.engine)
        self._update_rows_frame()

    def handle_select_priority(self, row_idx: int, new_priority: int):
        self.routine.elements[row_idx]["priority_level"] = new_priority
        self.routine.update_self_in_db(self.engine)
        self._update_rows_frame()


class RoutineConfigurer(SidebarExpansion):
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
            "fpath": ROUTINE_SVG_FPATH,
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
                title_save_button.on(
                    "click",
                    lambda: self.handle_title_update(self.title_input.value),
                )

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
                target_duration_slider.on(
                    "change",
                    lambda: self.handle_target_duration_update(
                        target_duration_slider.value
                    ),
                )
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
                target_duration_enabled_switch.on(
                    "click",
                    lambda: self.handle_target_duration_enabled_update(
                        target_duration_enabled_switch.value
                    ),
                )
            # bottom buttons
            ui.separator()
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                # start routine
                self.start_button = ui.button().classes("w-3/4")
                self.start_button.props(
                    f"icon={ICON_STRS.play} color=positive"
                )
                # delete routine
                self.delete_button = ui.button().classes("w-1/5")
                self.delete_button.props(
                    f"icon={ICON_STRS.delete} color=negative"
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


def routines_sidebar(engine: Engine, user: User):
    drawer = ui.left_drawer()
    drawer.classes(f"space-y-{V_SPACE} text-center py-0")
    drawer.props(f"breakpoint={BREAKPOINT} width={DRAWER_WIDTH} bordered")

    def handle_add_routine():
        # create the routine in the db
        new_routine = Routine()
        new_routine.add_self_to_db(engine)
        user.add_routine(engine, new_routine)
        # add the routine configurer to the drawer
        with routines_frame:
            RoutineConfigurer(
                engine=engine,
                user=user,
                routine=new_routine,
                parent_element=routines_frame,
            )

    with drawer:
        routines_frame = ui.element("div")
        with routines_frame:
            for routine in user.get_routines(engine):
                RoutineConfigurer(
                    engine=engine,
                    user=user,
                    routine=routine,
                    parent_element=routines_frame,
                )
        # add routine button
        ui.separator()
        add_routine_button = ui.button().classes("w-1/2")
        add_routine_button.props(f"icon={ICON_STRS.add}").on(
            "click", handle_add_routine
        )
    return drawer