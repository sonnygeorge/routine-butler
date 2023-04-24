import os
from typing import Callable, Optional, Union, List
from functools import partial
from copy import deepcopy

import asyncio
from loguru import logger
from fastapi import Request
from nicegui import ui
from sqlmodel import Session

from routine_butler.model.models import (
    Routine,
    Alarm,
    User,
)
from routine_butler.model.schema import (
    RoutineElement,
    RoutineReward,
    SoundFrequency,
    PriorityLevel,
)
from routine_butler.elements.primitives.svg import SVG
from routine_butler.elements.primitives.sidebar_expansion import (
    SidebarExpansion,
)

from routine_butler.utils.constants import clrs, icons  # TODO: use

DRAWER_WIDTH = "540"
DRAWER_BREAKPOINT = "0"
ROUTINE_SVG_SIZE: int = 28
PROGRAM_SVG_SIZE: int = 21
REWARD_SVG_SIZE: int = 17

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTINE_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/routine-icon.svg")
PROGRAM_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/program-icon.svg")
REWARD_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/reward-icon.svg")

V_SPACE = 4
DFLT_ROW_CLASSES = "justify-evenly items-center w-full px-4 pt-4"
DFLT_INPUT_PROPS = "standout dense"


class AlarmRow(ui.row):
    def __init__(self, alarm: Alarm, parent_element: ui.element):
        self.alarm = alarm
        self.parent_element = parent_element
        super().__init__()
        self.classes(DFLT_ROW_CLASSES + " gap-x-0")

        with self:
            # time input
            with ui.element("div").style("width: 23%;"):
                time_input = ui.input(value="12:00").classes("w-full")
                time_input.props(DFLT_INPUT_PROPS)
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
                                    time_input.value
                                ),
                            )
            # volume knob
            with ui.element("div").style("width: 10%;").classes("mx-1"):
                vol_knob = ui.knob(self.alarm.volume, track_color="grey-2")
                vol_knob.props("size=lg thickness=0.3")
                with vol_knob:
                    ui.icon("volume_up").props("size=xs")
                vol_knob.on(
                    "change",
                    lambda: self.handle_change_volume(vol_knob.value),
                )
            # sound frequency select
            with ui.element("div").style("width: 32%;"):
                sound_frequency_select = ui.select(
                    [e.value for e in SoundFrequency],
                    value=self.alarm.sound_frequency,
                    label="ring frequency",
                ).props(DFLT_INPUT_PROPS)
                sound_frequency_select.classes("w-full")
                sound_frequency_select.on(
                    "update:model-value",
                    lambda: self.handle_select_sound_frequency(
                        sound_frequency_select.value
                    ),
                )
            # toggle switch
            with ui.element("div").style("width: 34px;").classes("mx-1"):
                switch = ui.switch().props("dense")
                switch.on(
                    "click",
                    lambda: self.handle_toggle_enabled(switch.value),
                )
            # delete button
            self.delete_button = ui.button()
            self.delete_button.props("icon=cancel color=negative dense")
            self.delete_button.on("click", self.handle_delete)

    def handle_time_change(self, new_time):  # TODO: DB update
        self.alarm.set_time(new_time)

    def handle_change_volume(self, new_volume):  # TODO: DB update
        self.alarm.volume = new_volume

    def handle_select_sound_frequency(self, new_frequency):  # TODO: DB update
        self.alarm.sound_frequency = new_frequency

    def handle_toggle_enabled(self, value: bool):  # TODO: DB update
        self.alarm.enabled = value

    def handle_delete(self):  # TODO: DB update
        self.parent_element.remove(self)
        self.parent_element.update()
        del self


class AlarmsExpansion(SidebarExpansion):
    def __init__(self, routine: Routine):
        self.routine = routine
        super().__init__("Alarms", icon="alarm")

        with self:
            self.alarms_frame = ui.element("div")
            with self.alarms_frame:
                for alarm in self.routine.alarms:
                    AlarmRow(alarm=alarm, parent_element=self.alarms_frame)
            # add alarm button
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                self.add_alarm_button = ui.button().props("icon=add")
                self.add_alarm_button.classes("w-full")
                self.add_alarm_button.on("click", self.handle_add_alarm)

    def handle_add_alarm(self):  # TODO: DB update
        alarm = Alarm()
        self.routine.alarms.append(alarm)
        with self.alarms_frame:
            AlarmRow(alarm, parent_element=self.alarms_frame)


class RoutineElementsExpansion(SidebarExpansion):
    def __init__(self, engine, username: str, routine: Routine):
        self.engine = engine
        self.username = username
        self.routine = routine
        self.elements = routine.elements
        self.rewards = routine.rewards

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
                self.add_routine_element_button = ui.button().props("icon=add")
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

    def _update_rows_frame(self):
        """Clear and repopulates the 'div'/frame containing `RoutineElementRow`s
        in order to accomplish internal reording"""
        # remove any rows currently in the frame
        self.rows_frame.clear()
        # instantiate new rows within the frame
        with self.rows_frame:
            for idx, element in enumerate(self.elements):
                self._add_row(row_idx=idx, row_data=element)
            for idx, reward in enumerate(self.rewards):
                self._add_row(
                    row_idx=len(self.elements) + idx, row_data=reward
                )

    def _add_row(
        self, row_idx: int, row_data: Union[RoutineElement, RoutineReward]
    ):
        accent_color = (
            "primary" if "priority_level" in row_data.keys() else "secondary"
        )

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
            with Session(self.engine) as session:
                user = User()  # FIXME
            with ui.element("div").style("width: 32%;"):
                program_select = ui.select(
                    {p.id: p.title for p in user.programs},
                    value="",
                    label="program",
                ).props(DFLT_INPUT_PROPS)
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
                    ).props(DFLT_INPUT_PROPS)
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
                up_button.props(f"icon=arrow_upward dense")
                up_button.on(
                    "click",
                    lambda: self.handle_move_row_up(row_idx=row_idx),
                )
                down_button = ui.button().classes(f"bg-{accent_color}")
                down_button.props(f"icon=arrow_downward dense")
                down_button.on(
                    "click",
                    lambda: self.handle_move_row_down(row_idx=row_idx),
                )
            # delete button
            with ui.element("div").style("width: 7%;"):
                delete_button = ui.button()
                delete_button.props("icon=cancel color=negative dense")
                delete_button.on(
                    "click",
                    lambda: self.handle_delete_row(row_idx=row_idx),
                )

    def handle_add_element(self):
        element = {"priority_level": PriorityLevel.MEDIUM, "program": ""}
        self.elements.append(element)
        with Session(self.engine) as session:
            self.routine.update_in_db(session, elements=self.elements)
        if len(self.rewards) == 0:
            with self.rows_frame:
                self._add_row(row_idx=len(self.elements) - 1, row_data=element)
        else:
            self._update_rows_frame()

    def handle_add_reward(self):
        reward = {"program": ""}
        self.rewards.append(reward)
        with Session(self.engine) as session:
            self.routine.update_in_db(session, rewards=self.rewards)
        with self.rows_frame:
            new_row_idx = len(self.elements + self.rewards) - 1
            self._add_row(row_idx=new_row_idx, row_data=reward)

    def handle_move_row_up(self, row_idx: int):
        if row_idx == len(self.elements) or row_idx == 0:
            logger.debug("Cannot move upward")
            return
        elif row_idx > len(self.elements):  # reward
            self.rewards.insert(row_idx - 1, self.rewards.pop(row_idx))
            with Session(self.engine) as session:
                self.routine.update_in_db(session, elements=self.elements)
        else:  # element
            self.elements.insert(row_idx - 1, self.elements.pop(row_idx))
            with Session(self.engine) as session:
                self.routine.update_in_db(session, elements=self.elements)
        self._update_rows_frame()

    def handle_move_row_down(self, row_idx: int):
        if (
            row_idx == len(self.elements) - 1
            or row_idx == len(self.elements + self.rewards) - 1
        ):
            logger.debug("Cannot move downward")
            return
        elif row_idx >= len(self.elements):  # reward
            self.rewards.insert(row_idx + 1, self.rewards.pop(row_idx))
            with Session(self.engine) as session:
                self.routine.update_in_db(session, elements=self.elements)
        else:  # element
            self.elements.insert(row_idx + 1, self.elements.pop(row_idx))
            with Session(self.engine) as session:
                self.routine.update_in_db(session, elements=self.elements)
        self._update_rows_frame()

    def handle_delete_row(self, row_idx: int):
        if row_idx >= len(self.elements):  # reward
            self.rewards.pop(row_idx - len(self.elements))
            with Session(self.engine) as session:
                self.routine.update_in_db(session, rewards=self.rewards)
        else:  # element
            self.elements.pop(row_idx)
            with Session(self.engine) as session:
                self.routine.update_in_db(session, elements=self.elements)
        self._update_rows_frame()

    def handle_select_program(self, row_idx: int, new_program: int):
        if row_idx >= len(self.elements):  # reward
            self.rewards[row_idx - len(self.elements)]["program"] = new_program
            with Session(self.engine) as session:
                self.routine.update_in_db(session, rewards=self.rewards)
        else:  # element
            self.elements[row_idx]["program"] = new_program
            with Session(self.engine) as session:
                self.routine.update_in_db(session, elements=self.elements)
        self._update_rows_frame()

    def handle_select_priority(self, row_idx: int, new_priority: int):
        self.elements[row_idx]["priority_level"] = new_priority
        with Session(self.engine) as session:
            self.routine.update_in_db(session, elements=self.elements)
        self._update_rows_frame()


class RoutineConfigurer(SidebarExpansion):
    def __init__(
        self,
        engine,
        username: str,
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
                ).props(DFLT_INPUT_PROPS)
                # save button
                title_save_button = ui.button().props("icon=save")
                title_save_button.classes("w-1/5")
                title_save_button.on(
                    "click",
                    lambda: self.handle_title_update(self.title_input.value),
                )

            # alarms expansion
            with ui.row().classes(DFLT_ROW_CLASSES):
                AlarmsExpansion(routine)
            # routine elements expansion
            with ui.row().classes(DFLT_ROW_CLASSES):
                RoutineElementsExpansion(engine, username, routine)

            # row for target duration input
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE} no-wrap"):
                ui.label("Target Duration:").style("width: 120px;")
                # target duration slider
                target_duration_slider = ui.slider(
                    min=0, max=120, value=routine.target_duration
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
                target_duration_label.set_text(str(routine.target_duration))
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
                self.start_button.props("icon=play_arrow color=positive")
                # delete routine
                self.delete_button = ui.button().classes("w-1/5")
                self.delete_button.props("icon=cancel color=negative")
                self.delete_button.on("click", self.handle_delete)

    def handle_title_update(self, new_title):
        # update the title column in the db
        with Session(self.engine) as session:
            self.routine.update_in_db(session, title=new_title)
        # update the title in the expansion header
        self.header_label.set_text(new_title)

    def handle_target_duration_update(self, new_duration):
        # update the target_duration column in the db
        with Session(self.engine) as session:
            self.routine.update_in_db(session, target_duration=new_duration)

    def handle_target_duration_enabled_update(self, value: bool):
        # update the target_duration_enabled column in the db
        with Session(self.engine) as session:
            self.routine.update_in_db(session, target_duration_enabled=value)

    def handle_delete(self):
        # remove the expansion from the parent ui element
        self.parent_element.remove(self.expansion_frame)
        self.parent_element.update()
        # delete the routine from the db
        with Session(self.engine) as session:
            self.routine.delete_from_db(session)


def routines_drawer(engine, user: User):
    drawer = ui.left_drawer()
    drawer.classes(f"space-y-{V_SPACE} text-center py-0")
    drawer.props(
        f"breakpoint={DRAWER_BREAKPOINT} width={DRAWER_WIDTH} bordered"
    )

    def handle_add_routine():
        with Session(engine, expire_on_commit=False) as session:
            # create the routine in the db
            new_routine = Routine(user_username=user.username)
            new_routine.add_to_db(session)
            # add the routine configurer to the drawer
            with routines_frame:
                RoutineConfigurer(
                    engine=engine,
                    username=user.username,
                    routine=new_routine,
                    parent_element=routines_frame,
                )

    with drawer:
        routines_frame = ui.element("div")
        with routines_frame:
            for routine in user.routines:
                RoutineConfigurer(
                    engine=engine,
                    username=user.username,
                    routine=routine,
                    parent_element=routines_frame,
                )
        # add routine button
        ui.separator()
        add_routine_button = ui.button().classes("w-1/2")
        add_routine_button.props("icon=add").on("click", handle_add_routine)
    return drawer
