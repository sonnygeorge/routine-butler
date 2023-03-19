import remi

from components.primitive.centered_label import CenteredLabel
from components.scheduler import Scheduler
from schema.routine_configurations import RoutineConfigurations


class RoutineConfigurer(remi.gui.GridBox):
    """A component that offers controls to all of a Routine's configurations"""

    def __init__(self, routine_configuration: RoutineConfigurations):
        remi.gui.GridBox.__init__(
            self, width="100%", style={"box-sizing": "border-box"}
        )
        self.routine_configuration = routine_configuration

        self.css_border_color = "red"
        self.css_border_width = "2px"
        self.css_border_style = "solid"

        self.scheduler_label = CenteredLabel("Schedule:")
        self.scheduler = Scheduler(routine_configuration.schedule)

        self.define_grid([["scheduler_label", "scheduler"]])

        self.set_column_sizes(["30%", "70%"])
        self.set_style({"grid-template-rows": "50px"})

        self.append(self.scheduler_label, "scheduler_label")
        self.append(self.scheduler, "scheduler")

        # self.set_column_gap("0%")
        # self.set_row_gap("0%")
