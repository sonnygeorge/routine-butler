from typing import List, Optional, Tuple

from nicegui import ui

from routine_butler.constants import PagePath
from routine_butler.models.program import Program
from routine_butler.models.routine import Routine
from routine_butler.state import state
from routine_butler.utils import redirect_to_page


def get_programs_queues(
    routine: Routine,
) -> Tuple[List[Program], List[Program]]:
    element_program_titles = [e.program for e in routine.elements]
    reward_program_titles = [r.program for r in routine.rewards]
    user_programs = {p.title: p for p in state.user.get_programs(state.engine)}
    element_programs_queue = [user_programs[t] for t in element_program_titles]
    reward_programs_queue = [user_programs[t] for t in reward_program_titles]
    return element_programs_queue, reward_programs_queue


class RoutineAdministrator(ui.column):
    def __init__(self, routine: Routine):
        super().__init__()
        self.classes("absolute-center items-center justify-center")

        self.routine = routine
        queues = get_programs_queues(routine)
        self.element_programs_queue, self.reward_programs_queue = queues
        self._administer_next_program()

    @property
    def has_only_rewards_left_to_administer(self) -> bool:
        return (
            len(self.element_programs_queue) == 0
            and len(self.reward_programs_queue) > 0
        )

    @property
    def has_nothing_left_to_administer(self) -> bool:
        return (
            len(self.element_programs_queue) == 0
            and len(self.reward_programs_queue) == 0
        )

    @property
    def current_program(self) -> Optional[Program]:
        if self.has_nothing_left_to_administer:
            return None
        elif self.has_only_rewards_left_to_administer:
            return self.reward_programs_queue[0]
        else:
            return self.element_programs_queue[0]

    def _administer_next_program(self):
        if self.has_nothing_left_to_administer:
            redirect_to_page(PagePath.HOME)
            return

        with self:
            self.current_program.administer(
                on_complete=self.hdl_program_completion
            )

        if self.has_only_rewards_left_to_administer:
            with self:
                skip_button = ui.button("Skip Reward")
                skip_button.on("click", self.hdl_program_completion)

    def _pop_current_program_from_queue(self):
        if len(self.element_programs_queue) > 0:
            self.element_programs_queue.pop(0)
        elif len(self.reward_programs_queue) > 0:
            self.reward_programs_queue.pop(0)

    def hdl_program_completion(self):
        self.clear()  # clear current program ui
        self._pop_current_program_from_queue()  # remove program from queue
        self._administer_next_program()  # administer next program
