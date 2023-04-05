from typing import List, Optional
from abc import ABC, abstractmethod
from enum import Enum

from nicegui import ui
from loguru import logger

# import program_plugins
from routine_butler.database.models import Routine


# TODO: I have realized that the the nomenclature of program plugin is not needed here
# since any instantiated instance of a "program plugin" is a program. These are really
# just different types, and if with dependency injection + the unique run and unique
# config data are going to be JSONs in the database anyway (meaning we only ever need
# a programs table there), there is no need for the "plugin" nomenclature.

# TODO: Instead of having a constantly-checking timer, the "better" way would be to pass
# an "on completion" callback to each program. From this class we would pass it a
# `lambda: attempt_to_run_next_program(self)`. We can then forego this "status" business.

# TODO:
# - Run single program function
# - Put _ before private stuff


class RunnerStatus(Enum):
    NOT_RUNNING = "not running"
    RUNNING = "running"


class ProgramPluginStatus(Enum):
    NOT_INITIALIZED = "not initialized"
    INITIALIZED = "initialized"
    RUNNING = "running"
    COMPLETE = "complete"


class ProgramPlugin(ABC):
    @property
    @abstractmethod
    def initialized_program(self):
        pass

    @property
    @abstractmethod
    def status(self) -> ProgramPluginStatus:
        pass

    @abstractmethod
    def initialize(self, program, target_time: int):
        pass

    @abstractmethod
    def run_initialized_program(self):
        pass


OMIT_PROGRAM_FLAG = -1


class Runner(ui.element):
    def __init__(self):
        super().__init__("div")
        self.initialized_plugins_queue: List[ProgramPlugin] = []
        self.status = RunnerStatus.NOT_RUNNING
        self.timer = None

    @property
    def something_pending(self):
        return len(self.initialized_plugins_queue) > 0

    def run_routine(self, routine: Routine):
        # sort routine items by order index
        routine.routine_items.sort(key=lambda x: x.order_index)
        # calculate program target times
        target_times = self.generate_program_target_times(routine)
        # get and initialize program plugins
        self.initialized_plugins_queue = []
        for (routine_item, target_time) in zip(
            routine.routine_items, target_times
        ):
            if target_time != OMIT_PROGRAM_FLAG:
                program = routine_item.program
                plugin = self.get_plugin(program)
                plugin.initialize(program, target_time)
                self.initialized_plugins_queue.append(program)

        # begin timer
        self.timer = ui.timer(self.manage_current_ui, 1)

    def attempt_to_run_next_plugin(self):
        # clear ui
        self.clear()
        # if there are still plugins to run:
        if self.something_pending:
            # run next plugin
            self.initialized_plugins_queue[0].run_initialized_program()
        else:  # there are no more plugins to run
            # stop timer
            self.attempt_to_stop_timer()

    def manage_current_ui(self) -> bool:
        """Runs every time the timer ticks. Manages the current UI."""

        if not self.something_pending:
            self.attempt_to_stop_timer()
        else:
            cur_plugin = self.initialized_plugins_queue[0]

            # if starting up:
            if self.status == RunnerStatus.NOT_RUNNING:
                # run first plugin
                self.attempt_to_run_next_plugin()
                self.status = RunnerStatus.RUNNING  # change status

            # else if current plugin's program has been completed:
            elif cur_plugin.status == ProgramPluginStatus.COMPLETE:
                # remove the plugin from queue of pending plugins
                self.initialized_plugins_queue.pop(0)
                # attempt to run next plugin
                self.attempt_to_run_next_plugin()

    def generate_program_target_times(
        self, routine: Routine
    ) -> List[Optional[int]]:
        return [None for _ in routine.routine_items]

    def get_plugin(self, program) -> ProgramPlugin:
        pass

    def attempt_to_stop_timer(self):
        pass
