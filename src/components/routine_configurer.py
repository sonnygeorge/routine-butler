import remi

from components.primitives.centered_label import CenteredLabel
from components.primitives.button import Button
from components.scheduler import Scheduler
from database import Routine, Schedule, database


class RoutineConfigurer(remi.gui.VBox):
    """A component that offers controls to Configure a Routine"""

    def __init__(self, routine: Routine):
        remi.gui.VBox.__init__(self, width="100%")
        self.routine = routine

        self.css_border_color = "red"
        self.css_border_width = "2px"
        self.css_border_style = "solid"

        # schedulers
        self.schedulers = [Scheduler(schedule) for schedule in self.routine.schedules]
        self.scheduler_labels = [
            CenteredLabel(f"Schedule {i + 1}:") for i in range(len(self.schedulers))
        ]

        # schedulers grid
        self.schedulers_grid = remi.gui.GridBox(width="100%")
        self.append(self.schedulers_grid, "schedulers_grid")
        self.update_schedulers_grid()

        # add schedule button
        self.add_schedule_button = Button("Add Schedule")
        self.add_schedule_button.onclick.connect(self.on_add_schedule)
        self.append(self.add_schedule_button, "add_schedule_button")

    def on_add_schedule(self, widget):
        """add a new schedule to the routine"""
        self.routine.schedules.append(Schedule())
        self.schedulers.append(Scheduler(self.routine.schedules[-1]))
        self.scheduler_labels.append(
            CenteredLabel(f"Schedule {len(self.routine.schedules)}:")
        )
        self.update_schedulers_grid()

    def thoroughly_delete_schedule(
        self, scheduler_label: CenteredLabel, scheduler: Scheduler
    ):
        # remove from class lists
        self.scheduler_labels.remove(scheduler_label)
        self.schedulers.remove(scheduler)

        # remove from routine
        self.routine.schedules.remove(scheduler.schedule)

        # remove from database
        database.delete(scheduler.schedule)

    def check_and_clean_up_trashed_schedules(self):
        """if any of the schedulers have been trashed, remove them"""
        should_update_grid = False
        for scheduler_label, scheduler in zip(self.scheduler_labels, self.schedulers):
            if scheduler.trashed:
                self.thoroughly_delete_schedule(scheduler_label, scheduler)
                should_update_grid = True
        if should_update_grid:
            self.update_schedulers_grid()

    def update_schedulers_grid(self):
        """update the schedulers grid"""
        self.schedulers_grid.empty()

        grid_definition = [
            [f"scheduler_label_{i}", f"scheduler_{i}"]
            for i in range(len(self.schedulers))
        ]

        self.schedulers_grid.define_grid(grid_definition)
        self.schedulers_grid.set_column_sizes(["30%", "70%"])
        # this makes the rows the same height for each scheduler
        self.schedulers_grid.set_style(
            {"grid-template-rows": " ".join(["40px" for _ in self.schedulers])}
        )

        for i, (schedule_label, scheduler) in enumerate(
            zip(self.scheduler_labels, self.schedulers)
        ):
            self.schedulers_grid.append(schedule_label, f"scheduler_label_{i}")
            self.schedulers_grid.append(scheduler, f"scheduler_{i}")
