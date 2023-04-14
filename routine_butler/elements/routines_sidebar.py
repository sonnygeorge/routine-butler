import os
from typing import Callable, Optional, Union, List
from functools import partial

from loguru import logger
from fastapi import Request
from nicegui import ui
from sqlmodel import Session

from ..database.models import (
    Routine,
    RoutineItem,
    Alarm,
    SoundFrequency,
    PriorityLevel,
    User,
)
from routine_butler.elements.primitives.svg import SVG
from routine_butler.elements.primitives.sidebar_expansion import (
    SidebarExpansion,
)

from routine_butler.utils.constants import clrs, icons  # TODO: use

DRAWER_WIDTH = "500"
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


# TODO:
# - fix on click listeners for input elements and select elements
# - actually have program select element select from user's programs
# - use icon constants
# - connect everything to the database

# NICEGUI QUESTIONS
# - single-use timer w/ progress bar?


# def invoke_w_session(func: Callable, repository: Repository, *args, **kwargs):
#     with repository.session() as session:
#         return func(*args, **kwargs, session=session)


# class AlarmRow(ui.row):
#     def __init__(self, alarm: Alarm, parent_element: ui.element):
#         self.alarm = alarm
#         self.parent_element = parent_element
#         super().__init__()
#         self.classes(DFLT_ROW_CLASSES + " gap-x-0")

#         with self:
#             # time input
#             with ui.element("div").style("width: 23%;"):
#                 time_input = ui.input(value="12:00").classes("w-full")
#                 time_input.props(DFLT_INPUT_PROPS)
#                 with time_input as input:
#                     with input.add_slot("append"):
#                         icon = ui.icon("access_time").classes("cursor-pointer")
#                         icon.on("click", lambda: menu.open())
#                         with ui.menu() as menu:
#                             time_setter = ui.time()
#                             time_setter.bind_value(time_input)
#                             time_setter.on(
#                                 "update:model-value",
#                                 lambda: self.on_time_change(time_input.value),
#                             )
#             # volume knob
#             with ui.element("div").style("width: 10%;").classes("mx-1"):
#                 vol_knob = ui.knob(self.alarm.volume, track_color="grey-2")
#                 vol_knob.props("size=lg thickness=0.3")
#                 with vol_knob:
#                     ui.icon("volume_up").props("size=xs")
#                 vol_knob.on(
#                     "change", lambda: self.on_change_volume(vol_knob.value)
#                 )

#             # sound frequency select
#             with ui.element("div").style("width: 32%;"):
#                 sound_frequency_select = ui.select(
#                     [e.value for e in SoundFrequency],
#                     value=self.alarm.sound_frequency,
#                     label="ring frequency",
#                 ).props(DFLT_INPUT_PROPS)
#                 sound_frequency_select.classes("w-full")
#                 sound_frequency_select.on(
#                     "update:model-value",
#                     lambda: self.on_select_sound_frequency(
#                         sound_frequency_select.value
#                     ),
#                 )
#             # toggle switch
#             with ui.element("div").style("width: 34px;").classes("mx-1"):
#                 switch = ui.switch().props("dense")
#                 switch.on("click", lambda: self.on_toggle(switch.value))
#             # delete button
#             self.delete_button = ui.button()
#             self.delete_button.props("icon=cancel color=negative dense")
#             self.delete_button.on("click", self.on_delete)

#     def on_time_change(self, new_time):  # TODO: DB update
#         self.alarm.set_time(new_time)
#         logger.debug(f"Alarm {self.alarm.id} time changed to {new_time}")

#     def on_change_volume(self, new_volume):  # TODO: DB update
#         self.alarm.volume = new_volume
#         logger.debug(
#             f"Alarm {self.alarm.id} volume changed to " f"{new_volume}"
#         )

#     def on_select_sound_frequency(self, new_frequency):  # TODO: DB update
#         self.alarm.sound_frequency = new_frequency
#         logger.debug(
#             f"Alarm {self.alarm.id} sound frequency changed to {new_frequency}"
#         )

#     def on_toggle(self, value: bool):  # TODO: DB update
#         self.alarm.enabled = value
#         logger.debug(f"Alarm {self.alarm.id} enabled changed to {value}")

#     def on_delete(self):  # TODO: DB update
#         logger.debug(f"Deleting alarm {self.alarm.id}")
#         self.parent_element.remove(self)
#         self.parent_element.update()
#         del self


# class AlarmsExpansion(SidebarExpansion):
#     def __init__(self, routine: Routine):
#         self.routine = routine
#         super().__init__("Alarms", icon="alarm")

#         with self:
#             self.alarms_frame = ui.element("div")
#             with self.alarms_frame:
#                 for alarm in self.routine.alarms:
#                     AlarmRow(alarm=alarm, parent_element=self.alarms_frame)
#             # add alarm button
#             with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
#                 self.add_alarm_button = ui.button().props("icon=add")
#                 self.add_alarm_button.classes("w-full")
#                 self.add_alarm_button.on("click", self.on_add_alarm)

#     def on_add_alarm(self):  # TODO: DB update
#         logger.debug("Adding alarm")
#         alarm = Alarm()
#         self.routine.alarms.append(alarm)
#         with self.alarms_frame:
#             AlarmRow(alarm, parent_element=self.alarms_frame)


# class RoutineItemRow(ui.row):
#     def __init__(
#         self,
#         routine_item: RoutineItem,
#         repository: Repository,
#         parent_element: ui.element,
#     ):
#         self.routine_item = routine_item
#         self.parent_element = parent_element
#         self.repository = repository
#         # reload user from database to populate relationships
#         with repository.session() as session:
#             self.user = repository.eagerly_get_user(
#                 session=session, username=repository.current_username
#             )
#         super().__init__()
#         self.classes(DFLT_ROW_CLASSES + " gap-x-0")

#         btn_clr = "secondary" if self.routine_item.is_reward else "primary"

#         with self:
#             # number
#             number = ui.element("div").style("width: 5%;")
#             number.classes("mx-0 self-start w-full")
#             number.classes(f"rounded bg-{btn_clr} w-full drop-shadow")
#             with number:
#                 lbl = ui.label(f"{self.routine_item.order_index + 1}.")
#                 lbl.style("height: 1.125rem;")
#                 lbl.classes("text-white text-center text-xs text-bold")
#                 lbl.classes("flex items-center justify-center")
#             # program select
#             with ui.element("div").style("width: 32%;"):
#                 program_select = ui.select(
#                     self.user.programs,
#                     value="unlock box",  # TODO implement
#                     label="program",
#                 ).props(DFLT_INPUT_PROPS)
#                 program_select.classes("w-full")
#                 program_select.on(
#                     "update:model-value",
#                     lambda: self.on_select_program(program_select.value),
#                 )
#             # priority level select
#             with ui.element("div").style("width: 27%;"):
#                 if self.routine_item.is_reward:
#                     q_item = ui.element("q-item").props("dense")
#                     q_item.style("height: 2.5rem;")
#                     cls = "items-center justify-center border-secondary"
#                     cls += " rounded w-full border-dotted border-2"
#                     q_item.classes(cls)
#                     with q_item:
#                         SVG(
#                             REWARD_SVG_FPATH,
#                             size=REWARD_SVG_SIZE,
#                             color="#e5e5e5",
#                         )
#                 else:
#                     priority_level_select = ui.select(
#                         [e.value for e in PriorityLevel],
#                         value=self.routine_item.priority_level,
#                         label="priority",
#                     ).props(DFLT_INPUT_PROPS)
#                     priority_level_select.classes("w-full")
#                     priority_level_select.on(
#                         "update:model-value",
#                         lambda: self.on_select_priority_level(
#                             priority_level_select.value
#                         ),
#                     )
#             # order buttons
#             order_buttons_frame = ui.row().classes("gap-x-1 justify-center")
#             with order_buttons_frame.style("width: 18%;"):
#                 self.up_button = ui.button().classes(f"bg-{btn_clr}")
#                 self.up_button.props(f"icon=arrow_upward dense")
#                 self.down_button = ui.button().classes(f"bg-{btn_clr}")
#                 self.down_button.props(f"icon=arrow_downward dense")
#             # delete button
#             with ui.element("div").style("width: 7%;"):
#                 self.delete_button = ui.button()
#                 self.delete_button.props("icon=cancel color=negative dense")

#     def on_select_program(self, new_program):  # TODO: DB update
#         logger.debug(
#             f"Routine item {self.routine_item.id} program changed to {new_program}"
#         )
#         self.routine_item.program = new_program

#     def on_select_priority_level(self, new_priority_level):  # TODO: DB update
#         logger.debug(
#             f"Routine item {self.routine_item.id} priority level changed to "
#             f"{new_priority_level}"
#         )
#         self.routine_item.priority_level = new_priority_level


# class RoutineItemsExpansion(SidebarExpansion):
#     def __init__(self, routine: Routine, repository: Repository):
#         self.routine = routine
#         self.repository = repository
#         is_reg = [not ri.is_reward for ri in self.routine.routine_items]
#         self.last_reg_idx = sum(is_reg) - 1
#         svg_kwargs = {
#             "fpath": PROGRAM_SVG_FPATH,
#             "size": PROGRAM_SVG_SIZE,
#             "color": "black",
#         }
#         super().__init__("Chronology", icon=SVG, icon_kwargs=svg_kwargs)
#         self.classes("justify-between items-center")

#         with self:
#             self.items_frame = ui.element("div")
#             self._update_items_frame()

#             # bottom buttons
#             with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
#                 # add routine item button
#                 self.add_routine_item_button = ui.button().props("icon=add")
#                 self.add_routine_item_button.classes("w-3/4")
#                 self.add_routine_item_button.on(
#                     "click",
#                     lambda: invoke_w_session(
#                         self.add_routine_item, self.repository
#                     ),
#                 )
#                 # add reward buttom
#                 self.add_reward_button = ui.button().classes(
#                     "items-center w-1/5 bg-secondary"
#                 )
#                 with self.add_reward_button:
#                     SVG(REWARD_SVG_FPATH, size=REWARD_SVG_SIZE, color="white")
#                 self.add_reward_button.on(
#                     "click",
#                     lambda: invoke_w_session(
#                         self.add_reward_item, self.repository
#                     ),
#                 )

#     def add_routine_item(self, session: Session):
#         logger.debug("Adding routine item")
#         session.add(self.routine)
#         # create routine item to routine object with order index of the last_reg_idx + 1
#         routine_item = RoutineItem(order_index=self.last_reg_idx + 1)
#         # increment postceding (reward) routine items' order indexes
#         for ri in self.routine.routine_items:
#             if ri.order_index > self.last_reg_idx:
#                 ri.order_index += 1
#         # insert into list at new index
#         self.routine.routine_items.append(routine_item)
#         # update self.last_reg_idx
#         self.last_reg_idx += 1
#         logger.debug(f"Last regular routine item idx now: {self.last_reg_idx}")
#         if any(ri.is_reward for ri in self.routine.routine_items):
#             # update the frame if an insertion is being made
#             self._update_items_frame()
#         else:
#             # just add the row
#             with self.items_frame:
#                 self._add_row(routine_item)
#         # update db
#         session.commit()

#     def add_reward_item(self, session: Session):
#         logger.debug("Adding reward item")
#         session.add(self.routine)
#         # create routine object with order index of the last item + 1
#         routine_item = RoutineItem(
#             order_index=len(self.routine.routine_items), is_reward=True
#         )
#         self.routine.routine_items.append(routine_item)
#         with self.items_frame:
#             self._add_row(routine_item)
#         # update db
#         session.commit()

#     def move_item(  # TODO: DB update
#         self, routine_item: RoutineItem, up: bool = False, down: bool = False
#     ):
#         if up or down:
#             index = self.routine.routine_items.index(routine_item)
#             if up and (index == 0 or index == self.last_reg_idx + 1):
#                 logger.debug("Cannot move routine item upward")
#                 return
#             if down and (
#                 index >= len(self.routine.routine_items) - 1
#                 or index == self.last_reg_idx
#             ):
#                 logger.debug("Cannot move routine item downward")
#                 return
#             if up:
#                 idx1, idx2 = index - 1, index
#             elif down:
#                 idx1, idx2 = index, index + 1
#             self.routine.routine_items[idx1].order_index = idx2
#             self.routine.routine_items[idx2].order_index = idx1
#             logger.debug(f"Swapped routine item order indexes {idx1} & {idx2}")
#             self._update_items_frame()

#     def delete_item(self, routine_item: RoutineItem, session: Session):
#         session.add(routine_item)
#         session.add(self.routine)
#         logger.debug(f"Deleting routine item {routine_item.id}")
#         idx = self.routine.routine_items.index(routine_item)
#         self.routine.routine_items.pop(idx)
#         # update the order indexes of the routine items that came after the deleted one
#         for routine_item in self.routine.routine_items[idx:]:
#             routine_item.order_index -= 1
#         # update self.last_reg_idx
#         if idx <= self.last_reg_idx:
#             self.last_reg_idx -= 1
#         logger.debug(f"Last regular routine item idx now: {self.last_reg_idx}")
#         self._update_items_frame()
#         session.commit()

#     def _update_items_frame(self):
#         """Clear and repopulates the 'div'/frame containing `RoutineItemRow`s
#         in order to accomplish internal reording"""
#         # sort routine items in routine object by order index
#         self.routine.routine_items.sort(key=lambda x: x.order_index)
#         # remove any rows currently in the frame
#         self.items_frame.clear()
#         # instantiate new rows within the frame
#         with self.items_frame:
#             for routine_item in self.routine.routine_items:
#                 self._add_row(routine_item)

#     def _add_row(self, routine_item: RoutineItem):
#         row = RoutineItemRow(
#             routine_item=routine_item,
#             repository=self.repository,
#             parent_element=self.items_frame,
#         )
#         row.up_button.on(
#             "click",
#             lambda: self.move_item(row.routine_item, up=True),
#         )
#         row.down_button.on(
#             "click",
#             lambda: self.move_item(row.routine_item, down=True),
#         )
#         row.delete_button.on(
#             "click",
#             lambda: invoke_w_session(
#                 self.delete_item,
#                 repository=self.repository,
#                 routine_item=row.routine_item,
#             ),
#         )


class RoutineConfigurer(SidebarExpansion):
    def __init__(
        self,
        routine: Routine,
        user: User,
        parent_element: ui.element,
        session: Session,
    ):
        self.routine = routine
        self.user = user
        self.parent_element = parent_element
        self.session = session
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
                    value=self.routine.title,
                ).props(DFLT_INPUT_PROPS)
                # save button
                title_save_button = ui.button().props("icon=save")
                title_save_button.classes("w-1/5")
                title_save_button.on(
                    "click",
                    lambda: self.on_title_update(self.title_input.value),
                )

#             # alarms expansion
#             with ui.row().classes(DFLT_ROW_CLASSES):
#                 AlarmsExpansion(self.routine)
#             # routine items expansion
#             with ui.row().classes(DFLT_ROW_CLASSES):
#                 RoutineItemsExpansion(self.routine, self.repository)
#             # row for target duration input
#             with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE} no-wrap"):
#                 ui.label("Target Duration:").style("width: 120px;")
#                 # target duration slider
#                 target_duration_slider = ui.slider(
#                     min=0, max=120, value=self.routine.target_duration
#                 ).classes("w-1/3")
#                 target_duration_slider.on(
#                     "change",
#                     lambda: self.on_target_duration_change(
#                         target_duration_slider.value
#                     ),
#                 )
#                 # target duration label
#                 target_duration_label = ui.label().style("width: 35px;")
#                 target_duration_label.bind_text_from(
#                     target_duration_slider, "value"
#                 )
#                 target_duration_label.set_text(
#                     str(self.routine.target_duration)
#                 )
#                 ui.label("minutes").style("width: 52px;").classes("text-left")
#                 # target duration enabled toggle
#                 target_duration_toggle = ui.switch().props("dense")
#                 target_duration_toggle.on(
#                     "click",
#                     lambda: self.on_toggle_target_duration(
#                         target_duration_toggle.value
#                     ),
#                 )
#             # bottom buttons
#             ui.separator()
#             with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
#                 # start routine
#                 self.start_button = ui.button().classes("w-3/4")
#                 self.start_button.props("icon=play_arrow color=positive")
#                 # delete routine
#                 self.delete_button = ui.button().classes("w-1/5")
#                 self.delete_button.props("icon=cancel color=negative")
#                 self.delete_button.on("click", self.on_delete)

    def on_title_update(self, new_title):  # TODO: DB update
        logger.debug(
            f'Updating title of routine {self.routine.id} to "{new_title}"'
        )
        self.header_label.set_text(new_title)
        self.routine.title = new_title
        self.session.add(self.routine)
        self.session.commit()

#     def on_target_duration_change(self, new_duration):  # TODO: DB update
#         self.routine.target_duration = new_duration
#         logger.debug(
#             f"Target duration of routine {self.routine.id} changed to {new_duration}"
#         )

#     def on_toggle_target_duration(self, value: bool):  # TODO: DB update
#         self.routine.target_duration_enabled = value
#         logger.debug(
#             f"Target duration enabled of routine {self.routine.id} changed to {value}"
#         )

#     def on_delete(self):  # TODO: DB update
#         logger.debug(f"Deleting routine {self.routine.id}")
#         self.parent_element.remove(self.expansion_frame)
#         self.parent_element.update()
#         del self


class RoutinesSidebar(ui.left_drawer):
    def __init__(self, session: Session, user: User):
        self.session = session
        self.user = user
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
                        routine, self.user, parent_element=self.routines_frame, session=self.session
                    )
            # add routine button
            ui.separator()
            add_routine_button = ui.button().classes("w-1/2")
            add_routine_button.props("icon=add").on("click", self.add_routine)

    def add_routine(self):
        logger.debug("Adding routine for user: " + self.user.username)
        routine = Routine(user=self.user)
        self.session.add(routine)
        self.session.commit()
        with self.routines_frame:
            RoutineConfigurer(
                routine,
                self.user,
                parent_element=self.routines_frame,
                session=self.session,
            )
