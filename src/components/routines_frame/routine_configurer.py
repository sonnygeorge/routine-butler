import remi

from components.routines_frame.routine_programmer import RoutineProgrammer
from components.routines_frame.routine_scheduler import RoutineScheduler
from database import Routine, User


class RoutineConfigurer(remi.gui.VBox):
    """A component that offers controls to Configure a Routine"""

    def __init__(self, routine: Routine, user: User):
        self.routine = routine
        self.user = user
        remi.gui.VBox.__init__(self, width="100%")

        self.routine_scheduler = RoutineScheduler(self.routine)
        self.append(self.routine_scheduler, "routine_scheduler")

        self.routine_programmer = RoutineProgrammer(self.routine, self.user)
        self.append(self.routine_programmer, "routine_programmer")

    def idle(self):
        self.routine_scheduler.idle()
        self.routine_programmer.idle()
