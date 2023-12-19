import datetime
import random
from typing import List, Optional, Tuple

from loguru import logger
from nicegui import ui

from routine_butler.components import micro
from routine_butler.globals import G_SUITE_CREDENTIALS_MANAGER, PagePath
from routine_butler.models import PriorityLevel, Program, ProgramRun, Routine
from routine_butler.state import state
from routine_butler.utils.misc import redirect_to_page

ROUTINE_SVG_SIZE = 22
PROGRAM_SVG_SIZE = 19
REWARD_SVG_SIZE = 16.5
SVGS_COLOR = "black"
SVG_WIDTH_PX = 23
SDBR_FONT_PX = 12.5
SDBR_ROW_HEIGHT_PX = 28

LOAD_SECONDS_PER_PROGRAM = 2.5
TARGET_CUSHION_SECONDS = 90


def add_horizontal_dash() -> None:
    dash = ui.label("-").style(f"font-size: {SDBR_FONT_PX + 12}px")
    dash.classes("text-gray-600 font-medium")


def sidebar_row() -> ui.row:
    row = ui.row().style(f"height: {SDBR_ROW_HEIGHT_PX}px")
    row.classes("w-100 mx-3 justify-between items-center")
    return row


def sidebar_label(text: str) -> ui.label:
    label = ui.label(text).style(f"font-size: {SDBR_FONT_PX}px")
    label.classes("font-medium")
    return label


def prune_element_programs_to_target_duration(
    element_programs_queue: List[Program],
    element_program_priorities: List[PriorityLevel],
    target_duration_minutes: int,
) -> List[Program]:
    """Prunes the element programs queue to the target duration. Returns the pruned
    queue."""

    def merge_priority_dicts():
        merged = {}
        merged.update(low_priority_programs)
        merged.update(med_priority_programs)
        merged.update(high_priority_programs)
        return merged

    def total_expected_time_seconds():
        programs: List[Program] = merge_priority_dicts().values()
        return sum((p.estimate_duration_in_seconds() for p in programs))

    target_seconds = target_duration_minutes * 60
    loading_offset = LOAD_SECONDS_PER_PROGRAM * len(element_programs_queue)
    target_seconds -= loading_offset
    target_seconds -= TARGET_CUSHION_SECONDS

    low_priority_programs = {}
    med_priority_programs = {}
    high_priority_programs = {}
    for i, program in enumerate(element_programs_queue):
        if element_program_priorities[i] == PriorityLevel.LOW:
            low_priority_programs[i] = program
        elif element_program_priorities[i] == PriorityLevel.MEDIUM:
            med_priority_programs[i] = program
        else:
            high_priority_programs[i] = program

    pruned_titles = []
    while total_expected_time_seconds() >= target_seconds:
        if len(low_priority_programs) > 0:
            key_to_prune = random.sample(
                list(low_priority_programs.keys()), 1
            )[0]
            pruned_titles.append(low_priority_programs[key_to_prune].title)
            low_priority_programs.pop(key_to_prune)
        elif len(med_priority_programs) > 0:
            key_to_prune = random.sample(
                list(med_priority_programs.keys()), 1
            )[0]
            pruned_titles.append(med_priority_programs[key_to_prune].title)
            med_priority_programs.pop(key_to_prune)
        else:
            key_to_prune = random.sample(
                list(high_priority_programs.keys()), 1
            )[0]
            pruned_titles.append(high_priority_programs[key_to_prune].title)
            high_priority_programs.pop(key_to_prune)

    msg = f"Pruned {pruned_titles} to hit {target_duration_minutes} minutes."
    if len(pruned_titles) > 0:
        ui.timer(0.1, lambda: ui.notify(msg), once=True)

    merged = merge_priority_dicts()
    sorted_keys = sorted(merged.keys())
    return [merged[k] for k in sorted_keys]


def get_programs_queues(
    routine: Routine, target_duration_minutes: Optional[int] = None
) -> Tuple[List[Program], List[Program]]:
    element_program_titles = [e.program for e in routine.elements]
    element_program_priorities = [e.priority_level for e in routine.elements]
    reward_program_titles = [r.program for r in routine.rewards]
    user_programs = {p.title: p for p in state.user.get_programs(state.engine)}
    element_programs_queue = [user_programs[t] for t in element_program_titles]
    reward_programs_queue = [user_programs[t] for t in reward_program_titles]
    if target_duration_minutes is not None:
        element_programs_queue = prune_element_programs_to_target_duration(
            element_programs_queue,
            element_program_priorities,
            target_duration_minutes,
        )
    return element_programs_queue, reward_programs_queue


class RoutineAdministrator(ui.row):
    def __init__(self, routine: Routine):
        self.routine = routine
        if (
            self.routine.target_duration_enabled
            and state.element_programs_queue is None
        ):
            target_duration_minutes = self.routine.target_duration_minutes
        else:
            target_duration_minutes = None
        queues = get_programs_queues(routine, target_duration_minutes)
        
        if state.element_programs_queue is None:
            state.set_element_programs_queue(queues[0])
            self.element_programs_queue = queues[0]
        else:
            self.element_programs_queue = state.element_programs_queue
        
        self.reward_programs_queue = queues[1]

        n_element_programs = len(self.element_programs_queue)
        n_reward_programs = len(self.reward_programs_queue)
        self.n_programs_total = n_element_programs + n_reward_programs

        logger.info(
            f"(re-)Initializing RoutineAdministrator for {routine.title} w/ "
            f"{n_element_programs} element programs, {n_reward_programs} "
            f"reward programs, target duration: {target_duration_minutes}, & "
            f"{state.n_programs_traversed} programs traversed so far."
        )

        self.is_complete = False
        ui.timer(0.2, self.check_if_complete)

        super().__init__()
        self.classes("absolute-center items-center")
        self.classes("justify-center w-full space-x-6")

        with self:
            self.program_frame = ui.column()
            self.program_frame.classes("items-center justify-center")
        self.add_sidebar()

        if (
            state.n_programs_traversed == 0
            and state.pending_run_data_to_be_added_to_db is None
        ):
            ui.timer(0.1, self.begin_administration, once=True)
        else:  # Resuming mid-routine, presumably after a program completion
            self.on_program_completion()

    def check_if_complete(self):
        if self.is_complete:
            logger.info(f"Routine completed! ({self.routine.title})")
            redirect_to_page(PagePath.HOME)

    def add_sidebar(self):
        with self:
            sidebar = micro.card().classes("self-start bg-gray-100")
        with sidebar:
            with sidebar_row():
                with ui.column().style(f"width: {SVG_WIDTH_PX}px"):
                    micro.routine_svg(ROUTINE_SVG_SIZE, color=SVGS_COLOR)
                add_horizontal_dash()
                self.routine_label = sidebar_label(f"{self.routine.title}")
            ui.separator()

            with sidebar_row():
                self.program_svg_frame = ui.column()
                with self.program_svg_frame.style(f"width: {SVG_WIDTH_PX}px"):
                    micro.program_svg(PROGRAM_SVG_SIZE, color=SVGS_COLOR)
                add_horizontal_dash()
                self.program_label = sidebar_label(self.current_program.title)
            ui.separator()

            self.skip_button = ui.button("Skip").classes("bg-gray w-full")
            self.skip_button.disable()
            self.skip_button.style(f"height: {SDBR_ROW_HEIGHT_PX}px")
            self.skip_button.on("click", self._transition_to_next_program)
        self.update_sidebar()

    def update_sidebar(self):
        self.program_label.set_text(self.current_program.title)
        prog_str = (
            f"({state.n_programs_traversed + 1}/{self.n_programs_total})"
        )
        self.routine_label.set_text(f"{self.routine.title} {prog_str}")
        if self.has_only_rewards_left_to_administer:
            self.skip_button.enable()
            self.skip_button.update()
            self.program_svg_frame.clear()
            with self.program_svg_frame:
                micro.reward_svg(REWARD_SVG_SIZE, color=SVGS_COLOR)

    async def begin_administration(self):
        if G_SUITE_CREDENTIALS_MANAGER.validate_credentials():
            self._administer_next_program()
        else:
            await G_SUITE_CREDENTIALS_MANAGER.get_credentials()
            self._administer_next_program()

    @property
    def has_only_rewards_left_to_administer(self) -> bool:
        return state.n_programs_traversed >= len(self.element_programs_queue)

    @property
    def has_nothing_left_to_administer(self) -> bool:
        return state.n_programs_traversed == len(
            self.reward_programs_queue
        ) + len(self.element_programs_queue)

    @property
    def current_program(self) -> Optional[Program]:
        if self.has_nothing_left_to_administer:
            return None
        elif self.has_only_rewards_left_to_administer:
            idx = state.n_programs_traversed - len(self.element_programs_queue)
            return self.reward_programs_queue[idx]
        else:
            return self.element_programs_queue[state.n_programs_traversed]

    def _add_program_run_for_current_program_to_db(
        self, run_data: Optional[dict] = None
    ):
        current_program = self.current_program

        if state.pending_run_data_to_be_added_to_db is not None:
            run_data = state.pending_run_data_to_be_added_to_db
            state.set_pending_run_data_to_be_added_to_db(None)
        else:
            run_data = run_data or {}

        program_run = ProgramRun(
            program_title=current_program.title,
            plugin_type=current_program.plugin_type,
            plugin_dict=current_program.plugin_dict,
            routine_title=self.routine.title,
            start_time=state.current_program_start_time,
            end_time=datetime.datetime.now(),
            run_data=run_data,
            user_uid=state.user.uid,
        )
        program_run.add_self_to_db(state.engine)

    def _administer_next_program(self):
        if self.has_nothing_left_to_administer:
            state.set_element_programs_queue(None)
            state.set_n_programs_traversed(0)
            self.is_complete = True
        else:
            state.set_current_program_start_time(datetime.datetime.now())
            with self.program_frame:
                logger.info(f"Administering {self.current_program.title}...")
                self.current_program.administer(
                    on_complete=self.on_program_completion
                )
            self.update_sidebar()

    def _transition_to_next_program(self):
        self.program_frame.clear()  # clear current program frame ui
        state.set_n_programs_traversed(state.n_programs_traversed + 1)
        self._administer_next_program()  # administer next program

    def on_program_completion(self, run_data: Optional[dict] = None):
        self._add_program_run_for_current_program_to_db(run_data)  # record run
        self._transition_to_next_program()  # administer next program
