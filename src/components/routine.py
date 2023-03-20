import remi

from components.primitives.collapsible_vbox import CollapsibleVBox
from components.routine_configurer import RoutineConfigurer
from database import RoutineModel


class Routine(CollapsibleVBox):
    """
    Class for "Routine" objects

    A "Routine" is a self-managing chronology of "Programs" that can be scheduled
    to a time of day. For example, the user's morning "routine" might be comprised
    of a ReadText "Program" to read a motivational quote and a PromptContinue
    "Program" to prompt the user to drink a glass of water."
    """

    routine_model: RoutineModel

    def __init__(self, routine_model: RoutineModel = RoutineModel()):
        """In the GUI, a Routine is a CollapsibleVBox with logic to know what to render inside"""
        self.routine_model = routine_model
        CollapsibleVBox.__init__(self, title=self.routine_model.title)

        self.css_width = "78%"
        self.css_border_color = "yellow"
        self.css_border_width = "2px"
        self.css_border_style = "solid"

        self.routine_configurer = RoutineConfigurer(routine_model)
        self.append(self.routine_configurer)

    def should_be_on_screen(self):
        """Returns True if the Routine should be on screen, False otherwise"""
        # TODO: Implement this
        return True

    def update(self):
        pass
