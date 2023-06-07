from typing import Union

from nicegui import ui

from routine_butler.components import micro
from routine_butler.components.primitives import SVG, IconExpansion
from routine_butler.constants import ABS_PROGRAM_SVG_PATH, SDBR, SVG_SIZE
from routine_butler.models.routine import (
    Routine,
    RoutineElement,
    RoutineReward,
)
from routine_butler.state import state
from routine_butler.utils import move_down_in_list, move_up_in_list


class ElementsExpansion(IconExpansion):
    def __init__(self, routine: Routine):
        self.routine = routine

        svg_kwargs = {
            "fpath": ABS_PROGRAM_SVG_PATH,
            "size": SVG_SIZE.PROGRAM,
            "color": "black",
        }
        super().__init__("Chronology", icon=SVG, icon_kwargs=svg_kwargs)
        self.classes("justify-between items-center")

        with self:
            self.rows_frame = ui.element("div")
            self._update_rows_frame()

            with ui.row().classes(SDBR.DFLT_ROW_CLS + f" pb-{SDBR.V_SPACE}"):
                add_routine_element_button = micro.add_button().classes("w-64")
                add_reward_element_button = micro.reward_button().classes(
                    "w-64"
                )
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
        if isinstance(routine_element, RoutineReward):
            accent_color = "secondary"
        else:
            accent_color = "primary"

        with ui.row().classes("container flex justify-center p-1"):
            micro.row_superscript(row_superscript, accent_color)

            program_select = micro.program_select(
                state.program_titles, value=routine_element.program
            )

            if isinstance(routine_element, RoutineReward):
                with ui.row().classes(
                    "w-64 container flex justify-center items-center"
                ):
                    micro.reward_icon_placeholder()
            else:
                priority_level_select = micro.priority_level_select(
                    routine_element.priority_level
                )

            with ui.row().classes(
                "w-64 self-center	items-center justify-center"
            ):
                up_button, down_button = micro.order_buttons(accent_color)
                delete_button = micro.delete_button().props("dense")

            program_select.on(
                "update:model-value",
                lambda: self.hdl_select_program(
                    row_superscript, program_select.value
                ),
            )
            if not isinstance(routine_element, RoutineReward):
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
        new_element = RoutineElement()
        self.routine.elements.append(new_element)
        self.routine.update_self_in_db(state.engine)

        if len(self.routine.rewards) == 0:
            row_superscript = len(self.routine.elements + self.routine.rewards)
            with self.rows_frame:
                self._add_ui_row(row_superscript, new_element)
        else:
            self._update_rows_frame()

    def hdl_add_reward(self):
        new_reward = RoutineReward()
        self.routine.rewards.append(new_reward)
        self.routine.update_self_in_db(state.engine)

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
            self.routine.update_self_in_db(state.engine)
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
            self.routine.update_self_in_db(state.engine)
            self._update_rows_frame()

    def hdl_delete_row(self, row_superscript: int):
        if self._is_superscript_of_reward(row_superscript):
            idx = self._rewards_idx_from_row_superscript(row_superscript)
            self.routine.rewards.pop(idx)
        else:
            idx = self._elements_idx_from_row_superscript(row_superscript)
            self.routine.elements.pop(idx)
        self.routine.update_self_in_db(state.engine)
        self._update_rows_frame()

    def hdl_select_program(self, row_superscript: int, new_program: str):
        if self._is_superscript_of_reward(row_superscript):
            idx = self._rewards_idx_from_row_superscript(row_superscript)
            self.routine.rewards[idx].program = new_program
        else:
            idx = self._elements_idx_from_row_superscript(row_superscript)
            self.routine.elements[idx].program = new_program
        self.routine.update_self_in_db(state.engine)
        self._update_rows_frame()

    def hdl_select_priority(self, row_superscript: int, new_priority: int):
        idx = self._elements_idx_from_row_superscript(row_superscript)
        self.routine.elements[idx].priority_level = new_priority
        self.routine.update_self_in_db(state.engine)
        self._update_rows_frame()
