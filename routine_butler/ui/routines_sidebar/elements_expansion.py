from typing import Union

from loguru import logger
from nicegui import ui
from sqlalchemy.engine import Engine

from routine_butler.models.routine import (
    PriorityLevel,
    Routine,
    RoutineElement,
    RoutineReward,
)
from routine_butler.models.user import User
from routine_butler.ui.constants import (
    ABS_PROGRAM_SVG_PATH,
    ABS_REWARD_SVG_PATH,
    ICON_STRS,
    PROGRAM_SVG_SIZE,
    REWARD_SVG_SIZE,
)
from routine_butler.ui.constants import SDBR_DFLT_INPUT_PRPS as DFLT_INPUT_PRPS
from routine_butler.ui.constants import SDBR_DFLT_ROW_CLS as DFLT_ROW_CLASSES
from routine_butler.ui.constants import SDBR_V_SPACE as V_SPACE
from routine_butler.ui.primitives.icon_expansion import IconExpansion
from routine_butler.ui.primitives.svg import SVG


class ElementsExpansion(IconExpansion):
    def __init__(self, engine: Engine, user: User, routine: Routine):
        self.engine = engine
        self.user = user
        self.routine = routine

        svg_kwargs = {
            "fpath": ABS_PROGRAM_SVG_PATH,
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
                    SVG(
                        ABS_REWARD_SVG_PATH,
                        size=REWARD_SVG_SIZE,
                        color="white",
                    )
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
                            ABS_REWARD_SVG_PATH,
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
