import datetime
from typing import List, Optional, Tuple

from nicegui import ui

from routine_butler.components import micro
from routine_butler.globals import G_SUITE_CREDENTIALS_MANAGER, PagePath
from routine_butler.models import Program, ProgramRun, Routine
from routine_butler.state import state
from routine_butler.utils.misc import redirect_to_page

ROUTINE_SVG_SIZE = 22
PROGRAM_SVG_SIZE = 19
REWARD_SVG_SIZE = 16.5
SVGS_COLOR = "black"
SVG_WIDTH_PX = 23
SDBR_FONT_PX = 12.5
SDBR_ROW_HEIGHT_PX = 28


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


def get_programs_queues(
    routine: Routine,
) -> Tuple[List[Program], List[Program]]:
    element_program_titles = [e.program for e in routine.elements]
    reward_program_titles = [r.program for r in routine.rewards]
    user_programs = {p.title: p for p in state.user.get_programs(state.engine)}
    element_programs_queue = [user_programs[t] for t in element_program_titles]
    reward_programs_queue = [user_programs[t] for t in reward_program_titles]
    return element_programs_queue, reward_programs_queue


class RoutineAdministrator(ui.row):
    def __init__(self, routine: Routine):
        self.routine = routine
        queues = get_programs_queues(routine)
        self.element_programs_queue, self.reward_programs_queue = queues
        self.n_programs_traversed = 0
        self.n_programs_total = sum((len(q) for q in queues))

        super().__init__()
        self.classes("absolute-center items-center")
        self.classes("justify-center w-full space-x-6")

        with self:
            self.program_frame = ui.column()
        self.add_sidebar()

        ui.timer(0.1, self.begin_administration, once=True)

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
        prog_str = f"({self.n_programs_traversed + 1}/{self.n_programs_total})"
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

    def _pop_current_program_from_queue(self):
        if len(self.element_programs_queue) > 0:
            self.element_programs_queue.pop(0)
        elif len(self.reward_programs_queue) > 0:
            self.reward_programs_queue.pop(0)

    def _add_program_run_for_current_program_to_db(
        self, run_data: Optional[dict] = None
    ):
        current_program = self.current_program
        run_data = run_data or {}

        program_run = ProgramRun(
            program_title=current_program.title,
            plugin_type=current_program.plugin_type,
            plugin_dict=current_program.plugin_dict,
            routine_title=self.routine.title,
            start_time=self.current_program_start_time,
            end_time=datetime.datetime.now(),
            run_data=run_data,
            user_uid=state.user.uid,
        )
        program_run.add_self_to_db(state.engine)

    def _administer_next_program(self):
        if self.has_nothing_left_to_administer:
            redirect_to_page(PagePath.HOME)
            return
        self.current_program_start_time = datetime.datetime.now()
        with self.program_frame:
            self.current_program.administer(
                on_complete=self.on_program_completion
            )
        self.update_sidebar()

    def _transition_to_next_program(self):
        self.program_frame.clear()  # clear current program frame ui
        self._pop_current_program_from_queue()  # remove program from queue
        self.n_programs_traversed += 1
        self._administer_next_program()  # administer next program

    def on_program_completion(self, run_data: Optional[dict] = None):
        self._add_program_run_for_current_program_to_db(run_data)  # record run
        self._transition_to_next_program()  # administer next program
