from typing import Union

from nicegui import ui
from sqlalchemy.engine import Engine

from routine_butler.components import micro
from routine_butler.components.primitives.icon_expansion import IconExpansion
from routine_butler.components.primitives.svg import SVG
from routine_butler.constants import ABS_PROGRAM_SVG_PATH, PROGRAM_SVG_SIZE
from routine_butler.constants import SDBR_DFLT_ROW_CLS as DFLT_ROW_CLASSES
from routine_butler.constants import SDBR_V_SPACE as V_SPACE
from routine_butler.models.routine import (
    PriorityLevel,
    Routine,
    RoutineElement,
    RoutineReward,
)
from routine_butler.models.user import User
from routine_butler.utils import move_down_in_list, move_up_in_list

# since TypedDicts dont's support default values
DEFAULT_REWARD = {"program": ""}
DEFAULT_ELEMENT = {"priority_level": PriorityLevel.MEDIUM, "reward": ""}


class ElementsExpansion(IconExpansion):
    def __init__(self, engine: Engine, user: User, routine: Routine):
        self.engine = engine
        self.user = user
        self.routine = routine
        self.update_choosable_programs()

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

            with ui.row().classes(DFLT_ROW_CLASSES + f" pb-{V_SPACE}"):
                add_routine_element_button = micro.add_button()
                add_routine_element_button.classes("w-3/4")
                add_reward_element_button = micro.reward_button()
                add_reward_element_button.classes("w-1/5")
            add_routine_element_button.on("click", self.hdl_add_element)
            add_reward_element_button.on("click", self.hdl_add_reward)

    @property
    def num_elements(self):
        return len(self.routine.elements)

    def _update_rows_frame(self):
        """Clear and repopulates the 'div'/frame containing `RoutineElementRow`s
        in order to accomplish reording
        """
        self.rows_frame.clear()
        with self.rows_frame:
            for idx, element in enumerate(self.routine.elements):
                self._add_ui_row(
                    row_superscript=idx + 1, routine_element=element
                )
            for idx, reward in enumerate(self.routine.rewards):
                self._add_ui_row(
                    row_superscript=self.num_elements + idx + 1,
                    routine_element=reward,
                )

    def update_choosable_programs(self):
        self.choosable_programs = self.user.get_programs(self.engine)

    def _is_reward(
        self, routine_element: Union[RoutineElement, RoutineReward]
    ) -> bool:
        # TODO: a bit hacky since isinstance() doesn't work with TypedDicts
        return "priority_level" not in routine_element.keys()

    def _is_superscript_of_reward(self, row_superscript: int) -> bool:
        return row_superscript > self.num_elements

    def _elements_idx_from_row_superscript(self, row_superscript: int) -> int:
        return row_superscript - 1

    def _rewards_idx_from_row_superscript(self, row_superscript: int) -> int:
        return row_superscript - self.num_elements - 1

    def _add_ui_row(
        self,
        row_superscript: int,
        routine_element: Union[RoutineElement, RoutineReward],
    ):
        accent_color = (
            "secondary" if self._is_reward(routine_element) else "primary"
        )

        with ui.row().classes(DFLT_ROW_CLASSES + " gap-x-0"):
            micro.row_superscript(row_superscript, accent_color)
            with ui.element("div").style("width: 32%;"):
                program_select = micro.program_select(self.choosable_programs)
            with ui.element("div").style("width: 27%;"):
                if self._is_reward(routine_element):
                    micro.reward_icon_placeholder()
                else:
                    priority_level_select = micro.priority_level_select(
                        routine_element["priority_level"]
                    )
            up_button, down_button = micro.order_buttons(accent_color)
            with ui.element("div").style("width: 7%;"):
                delete_button = micro.delete_button().props("dense")

            program_select.on(
                "update:model-value",
                lambda: self.hdl_select_program(
                    row_superscript, program_select.value
                ),
            )
            if not self._is_reward(routine_element):
                priority_level_select.on(
                    "update:model-value",
                    lambda: self.hdl_select_priority(
                        row_superscript,
                        priority_level_select.value,
                    ),
                )
            down_button.on(
                "click", lambda: self.hdl_move_row_down(row_superscript)
            )
            up_button.on(
                "click", lambda: self.hdl_move_row_up(row_superscript)
            )
            delete_button.on(
                "click", lambda: self.hdl_delete_row(row_superscript)
            )

    def hdl_add_element(self):
        new_element = DEFAULT_ELEMENT.copy()
        self.routine.elements.append(new_element)
        self.routine.update_self_in_db(self.engine)

        if len(self.routine.rewards) == 0:
            row_superscript = len(self.routine.elements + self.routine.rewards)
            with self.rows_frame:
                self._add_ui_row(row_superscript, new_element)
        else:
            self._update_rows_frame()

    def hdl_add_reward(self):
        new_reward = DEFAULT_REWARD.copy()
        self.routine.rewards.append(new_reward)
        self.routine.update_self_in_db(self.engine)

        row_superscript = len(self.routine.elements + self.routine.rewards)
        with self.rows_frame:
            self._add_ui_row(row_superscript, new_reward)

    def _is_superscript_of_first_reward(self, row_superscript: int) -> bool:
        return row_superscript == self.num_elements + 1

    def _is_superscript_of_first_element(self, row_superscript: int) -> bool:
        return row_superscript == 1

    def hdl_move_row_up(self, row_superscript: int):
        is_movable = not self._is_superscript_of_first_reward(
            row_superscript
        ) and not self._is_superscript_of_first_element(row_superscript)

        if is_movable:
            if self._is_superscript_of_reward(row_superscript):
                idx = self._rewards_idx_from_row_superscript(row_superscript)
                move_up_in_list(self.routine.rewards, idx)
            else:
                idx = self._elements_idx_from_row_superscript(row_superscript)
                move_up_in_list(self.routine.elements, idx)
            self.routine.update_self_in_db(self.engine)
            self._update_rows_frame()

    def _is_superscript_of_last_reward(self, row_superscript: int) -> bool:
        return row_superscript == len(
            self.routine.elements + self.routine.rewards
        )

    def _is_superscript_of_last_element(self, row_superscript: int) -> bool:
        return row_superscript == self.num_elements

    def hdl_move_row_down(self, row_superscript: int):
        is_movable = not self._is_superscript_of_last_reward(
            row_superscript
        ) and not self._is_superscript_of_last_element(row_superscript)

        if is_movable:
            if self._is_superscript_of_reward(row_superscript):
                idx = self._rewards_idx_from_row_superscript(row_superscript)
                move_down_in_list(self.routine.rewards, idx)
            else:
                idx = self._elements_idx_from_row_superscript(row_superscript)
                move_down_in_list(self.routine.elements, idx)
            self.routine.update_self_in_db(self.engine)
            self._update_rows_frame()

    def hdl_delete_row(self, row_superscript: int):
        if self._is_superscript_of_reward(row_superscript):
            idx = self._rewards_idx_from_row_superscript(row_superscript)
            self.routine.rewards.pop(idx)
        else:
            idx = self._elements_idx_from_row_superscript(row_superscript)
            self.routine.elements.pop(idx)
        self.routine.update_self_in_db(self.engine)
        self._update_rows_frame()

    def hdl_select_program(self, row_superscript: int, new_program: str):
        if self._is_superscript_of_reward(row_superscript):
            idx = self._rewards_idx_from_row_superscript(row_superscript)
            self.routine.rewards[idx]["program"] = new_program
        else:
            idx = self._elements_idx_from_row_superscript(row_superscript)
            self.routine.elements[idx]["program"] = new_program
        self.routine.update_self_in_db(self.engine)
        self._update_rows_frame()

    def hdl_select_priority(self, row_superscript: int, new_priority: int):
        idx = self._elements_idx_from_row_superscript(row_superscript)
        self.routine.elements[idx]["priority_level"] = new_priority
        self.routine.update_self_in_db(self.engine)
        self._update_rows_frame()
