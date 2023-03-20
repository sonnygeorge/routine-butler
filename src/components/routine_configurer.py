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

        # schedulers
        self.schedulers = [
            Scheduler(schedule) for schedule in self.routine_model.schedules
        ]
        self.scheduler_labels = [
            CenteredLabel(f"Schedule {i + 1}:") for i in range(len(self.schedulers))
        ]
        grid_definition = [
            [f"scheduler_label_{i}", f"scheduler_{i}"]
            for i in range(len(self.schedulers))
        ]

        self.define_grid(grid_definition)
        self.set_column_sizes(["30%", "70%"])
        # this makes the rows the same height for each scheduler
        self.set_style(
            {"grid-template-rows": " ".join(["40px" for _ in self.schedulers])}
        )

        for i, (schedule_label, scheduler) in enumerate(
            zip(self.scheduler_labels, self.schedulers)
        ):
            self.append(schedule_label, f"scheduler_label_{i}")
            self.append(scheduler, f"scheduler_{i}")
