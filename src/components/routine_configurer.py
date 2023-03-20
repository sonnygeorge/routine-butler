import remi

from components.primitives.centered_label import CenteredLabel
from components.scheduler import Scheduler
from database import RoutineModel


class RoutineConfigurer(remi.gui.GridBox):
    """A component that offers controls to Configure a Routine"""

    def __init__(self, routine_model: RoutineModel):
        remi.gui.GridBox.__init__(
            self, width="100%", style={"box-sizing": "border-box"}
        )
        self.routine_model = routine_model

        self.css_border_color = "red"
        self.css_border_width = "2px"
        self.css_border_style = "solid"
        self.set_column_sizes(["30%", "70%"])
        self.set_style({"grid-template-rows": "50px"})

        # schedulers
        self.scheduler_label = CenteredLabel("Schedule:")
        self.schedulers = [
            Scheduler(schedule) for schedule in self.routine_model.schedules
        ]
        self.schedule_labels = [
            CenteredLabel(f"Schedule {i + 1}:") for i in range(len(self.schedulers))
        ]
        grid_definition = [["scheduler_label", "scheduler"]] * len(self.schedulers)

        self.define_grid(grid_definition)

        for schedule_label, scheduler in zip(self.schedule_labels, self.schedulers):
            self.append(schedule_label, "scheduler_label")
            self.append(scheduler, "scheduler")
