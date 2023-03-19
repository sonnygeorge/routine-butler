import remi

from components.primitives.collapsible_vbox import CollapsibleVBox
from components.routine_configurer import RoutineConfigurer
from schema.routine_configurations import RoutineConfigurations


class Routine(CollapsibleVBox):
    def __init__(self, routine_configurations: RoutineConfigurations):
        CollapsibleVBox.__init__(self, title = routine_configurations.routine_id)
        self.routine_configurations = routine_configurations

        self.css_width = "78%"

        self.css_border_color = "yellow"
        self.css_border_width = "2px"
        self.css_border_style = "solid"

        self.routine_configurer = RoutineConfigurer(routine_configurations)
        self.append(self.routine_configurer)

    def should_be_on_stage(self):
        # TODO: Implement this
        return True

    def update(self):
        pass
