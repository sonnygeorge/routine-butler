from typing import List, Tuple

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


class RoutineAdministrator(ui.element):
    def __init__(self, routine: Routine):
        super().__init__("div")
        self.routine = routine
        queues = get_programs_queues(routine)
        self.element_programs_queue, self.reward_programs_queue = queues
        self._administer_next_program()

    def _administer_next_program(self):
        if len(self.element_programs_queue) > 0:
            program = self.element_programs_queue[0]
        elif len(self.reward_programs_queue) > 0:
            with self:
                skip_button = ui.button("Skip Reward")
            skip_button.on("click", self.hdle_program_completion)
            program = self.reward_programs_queue[0]
        else:  # routine is complete
            redirect_to_page(PagePath.HOME)
            return
        with self:
            program.administer(on_complete=self.hdle_program_completion)

    def _pop_from_queue(self):
        if len(self.element_programs_queue) > 0:
            self.element_programs_queue.pop(0)
        elif len(self.reward_programs_queue) > 0:
            self.reward_programs_queue.pop(0)

    def hdle_program_completion(self):
        self.clear()  # remove current program ui
        self._pop_from_queue()  # remove current program from queue
        self._administer_next_program()  # administer next program
