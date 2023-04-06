import os
from typing import Callable, Optional, Union, List

from loguru import logger
from nicegui import ui

from routine_butler.database.models import (
    Routine,
    RoutineItem,
    Alarm,
    SoundInterval,
    PriorityLevel,
    User,
)
from routine_butler.database.repository import Repository
from routine_butler.elements.primitives.svg import SVG
from routine_butler.elements.primitives.sidebar_expansion import SidebarExpansion

from routine_butler.utils.constants import clrs, icons  # TODO: use

DRAWER_WIDTH = "500"
DRAWER_BREAKPOINT = "0"
ROUTINES_SVG_SIZE: int = 28
PROGRAMS_SVG_SIZE: int = 26

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ROUTINE_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/routine-icon.svg")
PROGRAM_SVG_FPATH = os.path.join(CURRENT_DIR, "../assets/program-icon.svg")

V_SPACE = 4
DFLT_ROW_CLASSES = "justify-evenly items-center w-full px-4 pt-4"
DFLT_INPUT_PROPS = "standout dense"


# TODO:
# - add an is reward checkbox to final routine item... or just a reward slot?
# - fix on click listeners for input elements and select elements
# - actually have program select element select from user's programs
# - use icon constants
# - connect everything to the database

# NICEGUI QUESTIONS
# - single-use timer w/ progress bar?


class AlarmSetter(ui.row):
    def __init__(self, alarm: Alarm, parent_element: ui.element):
        self.alarm = alarm
        self.parent_element = parent_element

        super().__init__()
        self.classes(DFLT_ROW_CLASSES + " no-wrap")

        with self:
            # time input
            time_input = ui.input(value="12:00").style("width: 90px;")
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
                            lambda: self.on_time_change(time_input.value),
                        )

            # volume knob
            vol_knob = ui.knob(self.alarm.volume, track_color="grey-2")
            vol_knob.props("size=lg thickness=0.3")
            with vol_knob:
                ui.icon("volume_up").props("size=xs")
            vol_knob.on(
                "change", lambda: self.on_change_volume(vol_knob.value)
            )

            # sound interval select
            sound_interval_select = ui.select(
                [e.value for e in SoundInterval],
                value=self.alarm.sound_interval,
            ).props(DFLT_INPUT_PROPS, remove="label")
            sound_interval_select.classes("w-1/4").style("width: 120px;")
            sound_interval_select.on(
                "update:model-value",
                lambda: self.on_select_sound_interval(
                    sound_interval_select.value
                ),
            )

            # toggle switch
            switch = ui.switch().props("dense")
            switch.on("click", lambda: self.on_toggle(switch.value))

            # delete button
            self.delete_button = ui.button()
            self.delete_button.props("icon=cancel color=negative dense")
            self.delete_button.on("click", self.on_delete)

    def on_time_change(self, new_time):  # TODO: DB update
        self.alarm.set_time(new_time)
        logger.debug(f"Alarm {self.alarm.id} time changed to {new_time}")

    def on_change_volume(self, new_volume):  # TODO: DB update
        self.alarm.volume = new_volume
        logger.debug(
            f"Alarm {self.alarm.id} volume changed to " f"{new_volume}"
        )

    def on_select_sound_interval(self, new_interval):  # TODO: DB update
        self.alarm.sound_interval = new_interval
        logger.debug(
            f"Alarm {self.alarm.id} sound interval changed to {new_interval}"
        )

    def on_toggle(self, value: bool):  # TODO: DB update
        self.alarm.enabled = value
        logger.debug(f"Alarm {self.alarm.id} enabled changed to {value}")

    def on_delete(self):  # TODO: DB update
        logger.debug(f"Deleting alarm {self.alarm.id}")
        self.parent_element.remove(self)
        self.parent_element.update()
        del self


class AlarmsConfigurer(SidebarExpansion):
    def __init__(self, routine: Routine):
        self.routine = routine

        super().__init__("Alarms", icon="alarm")

        with self:
            self.alarms_frame = ui.element("div")
            with self.alarms_frame:
                for alarm in self.routine.alarms:
                    AlarmSetter(alarm=alarm, parent_element=self.alarms_frame)
            # add alarm button
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                self.add_alarm_button = ui.button().props("icon=add")
                self.add_alarm_button.classes("w-full")
                self.add_alarm_button.on("click", self.on_add_alarm)

    def on_add_alarm(self):  # TODO: DB update
        logger.debug("Adding alarm")
        alarm = Alarm()
        self.routine.alarms.append(alarm)
        with self.alarms_frame:
            AlarmSetter(alarm, parent_element=self.alarms_frame)


class RoutineItemSetter(ui.row):
    def __init__(
        self, routine_item: RoutineItem, user: User, parent_element: ui.element
    ):
        self.routine_item = routine_item
        self.parent_element = parent_element

        super().__init__()
        self.classes(DFLT_ROW_CLASSES + " no-wrap space-x-0")

        with self:
            # program select
            program_select = ui.select(
                user.programs,
                value="unlock box",
            ).props(DFLT_INPUT_PROPS, remove="label")
            program_select.classes("w-1/4").style("width: 120px;")
            program_select.on(
                "update:model-value",
                lambda: self.on_select_program(program_select.value),
            )

            # priority level select
            priority_level_select = ui.select(
                [e.value for e in PriorityLevel],
                value=self.routine_item.priority_level,
            ).props(DFLT_INPUT_PROPS, remove="label")
            priority_level_select.classes("w-1/4").style("width: 120px;")
            priority_level_select.on(
                "update:model-value",
                lambda: self.on_select_priority_level(
                    priority_level_select.value
                ),
            )

            # order buttons
            self.up_button = ui.button().props("icon=arrow_upward dense")
            self.down_button = ui.button().props("icon=arrow_downward dense")

            # delete button
            self.delete_button = ui.button()
            self.delete_button.props("icon=cancel color=negative dense")

    def on_select_program(self, new_program):  # TODO: DB update
        logger.debug(
            f"Routine item {self.routine_item.id} program changed to {new_program}"
        )
        self.routine_item.program = new_program

    def on_select_priority_level(self, new_priority_level):  # TODO: DB update
        logger.debug(
            f"Routine item {self.routine_item.id} priority level changed to "
            f"{new_priority_level}"
        )
        self.routine_item.priority_level = new_priority_level


class RoutineItemsConfigurer(SidebarExpansion):
    def __init__(self, routine: Routine, user: User):
        self.routine = routine
        self.user = user

        super().__init__("Program Chronology", icon="list")
        self.classes("justify-between items-center")

        with self:
            self.routine_items_frame = ui.element("div")
            self.update_routine_items_frame()

            # add routine item button
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                self.add_routine_item_button = ui.button().props("icon=add")
                self.add_routine_item_button.classes("w-full")
                self.add_routine_item_button.on(
                    "click", self.on_add_routine_item
                )

    def update_routine_items_frame(self):
        # sort routine items in routine object by order index
        self.routine.routine_items.sort(key=lambda x: x.order_index)
        # remove any setters in frame
        self.routine_items_frame.clear()
        # create new setters and add them to frame
        with self.routine_items_frame:
            for routine_item in self.routine.routine_items:
                self._add_setter(routine_item)

    def move_routine_item(  # TODO: DB update
        self, setter: RoutineItemSetter, up: bool = False, down: bool = False
    ):
        if up or down:
            index = self.routine.routine_items.index(setter.routine_item)
            if up and index == 0:
                logger.debug("Cannot move routine item upward")
                return
            if down and index >= len(self.routine.routine_items) - 1:
                logger.debug("Cannot move routine item downward")
                return
            if up:
                idx1, idx2 = index - 1, index
            elif down:
                idx1, idx2 = index, index + 1
            self.routine.routine_items[idx1].order_index = idx2
            self.routine.routine_items[idx2].order_index = idx1
            logger.debug(f"Swapped routine item order indexes {idx1} & {idx2}")
            self.update_routine_items_frame()

    # TODO: DB update
    def on_delete_routine_item(self, setter: RoutineItemSetter):
        logger.debug(f"Deleting routine item {setter.routine_item.id}")
        # remove routine item from routine object
        idx = self.routine.routine_items.index(setter.routine_item)
        self.routine.routine_items.pop(idx)
        # update the order indexes of the routine items that came after the deleted one
        for routine_item in self.routine.routine_items[idx:]:
            routine_item.order_index -= 1
        # remove setter from frame
        self.routine_items_frame.remove(setter)

    def on_add_routine_item(self):  # TODO: DB update
        logger.debug("Adding routine item")
        # add routine item to routine object with order index of the last item + 1
        routine_item = RoutineItem(order_index=len(self.routine.routine_items))
        self.routine.routine_items.append(routine_item)
        with self.routine_items_frame:
            self._add_setter(routine_item)

    def _add_setter(self, routine_item: RoutineItem):
        setter = RoutineItemSetter(
            routine_item=routine_item,
            user=self.user,
            parent_element=self.routine_items_frame,
        )
        setter.up_button.on(
            "click", lambda e: self.move_routine_item(setter, up=True)
        )
        setter.down_button.on(
            "click", lambda e: self.move_routine_item(setter, down=True)
        )
        setter.delete_button.on(
            "click", lambda: self.on_delete_routine_item(setter)
        )


class RoutineConfigurer(SidebarExpansion):
    def __init__(
        self, routine: Routine, user: User, parent_element: ui.element
    ):
        self.routine = routine
        self.user = user
        self.parent_element = parent_element

        svg_kwargs = {
            "fpath": ROUTINE_SVG_FPATH,
            "size": ROUTINES_SVG_SIZE,
            "color": "black",
        }
        super().__init__(routine.title, icon=SVG, icon_kwargs=svg_kwargs)
        self.frame.classes(f"mt-{V_SPACE}")

        with self:
            # top row for setting title
            with ui.row().classes(DFLT_ROW_CLASSES):
                ui.label("Title:")
                # title input
                self.title_input = ui.input(
                    value=self.routine.title,
                ).props(DFLT_INPUT_PROPS)
                # save button
                title_save_button = ui.button().props("icon=save")
                title_save_button.classes("w-1/5")
                title_save_button.on(
                    "click",
                    lambda: self.on_title_update(self.title_input.value),
                )

            # alarms configurer
            with ui.row().classes(DFLT_ROW_CLASSES):
                AlarmsConfigurer(self.routine)

            # routine items configurer
            with ui.row().classes(DFLT_ROW_CLASSES):
                RoutineItemsConfigurer(self.routine, self.user)

            # row for target duration input
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE} no-wrap"):
                ui.label("Target Duration:").style("width: 120px;")
                # target duration slider
                target_duration_slider = ui.slider(
                    min=0, max=120, value=self.routine.target_duration
                ).classes("w-1/3")
                target_duration_slider.on(
                    "change",
                    lambda: self.on_target_duration_change(
                        target_duration_slider.value
                    ),
                )
                # target duration label
                target_duration_label = ui.label().style("width: 35px;")
                target_duration_label.bind_text_from(
                    target_duration_slider, "value"
                )
                target_duration_label.set_text(
                    str(self.routine.target_duration)
                )
                ui.label("minutes").style("width: 52px;").classes("text-left")
                # target duration enabled toggle
                target_duration_toggle = ui.switch().props("dense")
                target_duration_toggle.on(
                    "click",
                    lambda: self.on_toggle_target_duration(
                        target_duration_toggle.value
                    ),
                )

            ui.separator()

            # bottom buttons
            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                # start routine
                self.start_button = ui.button().classes("w-3/4")
                self.start_button.props("icon=play_arrow color=positive")
                # delete routine
                self.delete_button = ui.button().classes("w-1/5")
                self.delete_button.props("icon=cancel color=negative")
                self.delete_button.on("click", self.on_delete)

    def on_title_update(self, new_title):  # TODO: DB update
        logger.debug(
            f'Updating title of routine {self.routine.id} to "{new_title}"'
        )
        self.header_label.set_text(new_title)

    def on_target_duration_change(self, new_duration):  # TODO: DB update
        self.routine.target_duration = new_duration
        logger.debug(
            f"Target duration of routine {self.routine.id} changed to {new_duration}"
        )

    def on_toggle_target_duration(self, value: bool):  # TODO: DB update
        self.routine.target_duration_enabled = value
        logger.debug(
            f"Target duration enabled of routine {self.routine.id} changed to {value}"
        )

    def on_delete(self):  # TODO: DB update
        logger.debug(f"Deleting routine {self.routine.id}")
        self.parent_element.remove(self.frame)
        self.parent_element.update()
        del self


class RoutinesSidebar(ui.left_drawer):
    def __init__(self, user: User, repository: Repository):
        self.user = user
        self.repository = repository

        super().__init__()
        self.classes(f"space-y-{V_SPACE} text-center py-0")
        self.props(
            f"breakpoint={DRAWER_BREAKPOINT} width={DRAWER_WIDTH} bordered"
        )

        with self:
            self.routines_frame = ui.element("div")
            with self.routines_frame:
                for routine in self.user.routines:
                    RoutineConfigurer(
                        routine, self.user, parent_element=self.routines_frame
                    )

            ui.separator()

            # add routine button
            add_routine_button = ui.button().classes("w-1/2").props("icon=add")
            add_routine_button.on("click", self.add_routine)

    def add_routine(self):  # TODO: DB update
        logger.debug("Adding routine")
        routine = Routine()
        self.user.routines.append(routine)
        with self.routines_frame:
            RoutineConfigurer(
                routine, self.user, parent_element=self.routines_frame
            )
