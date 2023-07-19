from typing import Union

from nicegui import ui

from routine_butler.components import micro
from routine_butler.models import (
    PriorityLevel,
    Routine,
    RoutineElement,
    RoutineReward,
)
from routine_butler.state import state
from routine_butler.utils.misc import move_down_in_list, move_up_in_list


class ChronologyConfigurer(micro.ExpandableCard):
    def __init__(self, routine: Routine):
        self.routine = routine

        program_svg_kwargs = {"size": 21, "color": "lightgray"}
        super().__init__(
            "Chronology",
            icon=micro.program_svg,
            icon_kwargs=program_svg_kwargs,
            width="850px",
        )

        with self:
            self.rows_frame = ui.column()
            self.rows_frame.classes("items-center justify-center pt-4")
            self._update_ui()

    @property
    def num_elements(self):
        return len(self.routine.elements)

    def _add_bottom_buttons_to_ui(self):
        with ui.row().classes("mb-4"):
            add_routine_element_button = micro.add_button().classes("w-40")
            ui.separator().props("vertical").classes("mx-3 bg-gray-100")
            add_reward_element_button = micro.reward_button().classes("w-40")

        add_routine_element_button.on("click", self.hdl_add_element)
        add_reward_element_button.on("click", self.hdl_add_reward)

    def _update_ui(self):
        """Clear and repopulates the 'div'/frame containing `RoutineElementRow`s"""
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

            self._add_bottom_buttons_to_ui()

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

        row = ui.row().classes("container flex justify-between items-center")
        with row.classes("px-4 gap-x-2").style("width: 800px"):
            micro.row_superscript(row_superscript, accent_color)
            program_select = micro.program_select(
                value=routine_element.program,
                program_titles=state.program_titles,
            )
            if isinstance(routine_element, RoutineReward):
                micro.reward_icon_placeholder()
            else:
                priority_level_select = micro.priority_level_select(
                    value=routine_element.priority_level,
                    priority_levels=PriorityLevel,
                )
            up_button, down_button = micro.order_buttons(accent_color)
            delete_button = micro.delete_button().props("dense")
            delete_button.classes("w-12")

        ui.separator().classes("bg-gray-100 w-full")

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
        up_button.on("click", lambda: self.hdl_move_row_up(row_superscript))
        delete_button.on("click", lambda: self.hdl_delete_row(row_superscript))

    def hdl_add_element(self):
        new_element = RoutineElement()
        self.routine.elements.append(new_element)
        self.routine.update_self_in_db(state.engine)
        self._update_ui()

    def hdl_add_reward(self):
        new_reward = RoutineReward()
        self.routine.rewards.append(new_reward)
        self.routine.update_self_in_db(state.engine)
        self._update_ui()

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
            self._update_ui()

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
            self._update_ui()

    def hdl_delete_row(self, row_superscript: int):
        if self._is_superscript_of_reward(row_superscript):
            idx = self._rewards_idx_from_row_superscript(row_superscript)
            self.routine.rewards.pop(idx)
        else:
            idx = self._elements_idx_from_row_superscript(row_superscript)
            self.routine.elements.pop(idx)
        self.routine.update_self_in_db(state.engine)
        self._update_ui()

    def hdl_select_program(self, row_superscript: int, new_program: str):
        if self._is_superscript_of_reward(row_superscript):
            idx = self._rewards_idx_from_row_superscript(row_superscript)
            self.routine.rewards[idx].program = new_program
        else:
            idx = self._elements_idx_from_row_superscript(row_superscript)
            self.routine.elements[idx].program = new_program
        self.routine.update_self_in_db(state.engine)
        self._update_ui()

    def hdl_select_priority(self, row_superscript: int, new_priority: int):
        idx = self._elements_idx_from_row_superscript(row_superscript)
        self.routine.elements[idx].priority_level = new_priority
        self.routine.update_self_in_db(state.engine)
        self._update_ui()
