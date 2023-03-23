import remi
from loguru import logger

from components.primitives.button import Button
from components.routine_component import RoutineComponent
from models import Routine, User

MARGIN = "23px 23px 23px 23px"


class RoutinesContainer(remi.gui.VBox):
    """VBox-style container for the routine components of the app."""

    user: User
    routine_components: list[RoutineComponent] = []

    def __init__(self, user):
        remi.gui.VBox.__init__(
            self,
            width="100%",
            style={
                "margin": "5px",
                "background": "none",
                "justify-content": "space-between",
            },
        )
        self.user = user

        # routines
        self.routines_vbox = remi.gui.VBox(
            width="100%",
            style={
                "margin": MARGIN,
                "background": "none",
                "justify-content": "space-between",
            },
        )
        self.routines_vbox.css_background_color = "transparent"
        self.append(self.routines_vbox, "routines_vbox")

        self.instantiate_routine_components()
        self.manage_routine_components_and_run_idle_funcs()

        # add routine button
        self.add_routine_button = Button(
            "+", style={"margin": MARGIN, "font-size": "30px"}
        )
        self.add_routine_button.css_width = "9%"
        self.add_routine_button.onclick.connect(self.on_add_routine)
        self.append(self.add_routine_button, "add_routine_button")

    def instantiate_routine_components(self):
        """Instantiates the routines from user's routines"""
        for routine in self.user.routines:
            self.routine_components.append(RoutineComponent(routine))

    def idle(self):
        """Called every update_interval seconds."""
        self.manage_routine_components_and_run_idle_funcs()

    def manage_routine_components_and_run_idle_funcs(self):
        """Adds/removes routine components and runs their idle functions"""
        for routine_component in self.routine_components:
            # if routine component should be on the screen and is not already
            if (
                routine_component.should_be_on_screen()
                and routine_component
                not in self.routines_vbox.children.values()
            ):
                self.routines_vbox.append(
                    routine_component, key=routine_component.routine.id
                )
                routine_component.idle()

            # if routine component should not be on the screen and is already
            elif (
                not routine_component.should_be_on_screen()
                and routine_component in self.routines_vbox.children.values()
            ):
                self.routines_vbox.remove_child(routine_component)
            # if routine component should be on the screen and is already
            else:
                routine_component.idle()

    def on_add_routine(self, widget):
        """Called when the user clicks on the add_routine_button."""
        logger.debug("Adding new routine")

        # create new routine
        routine = Routine()

        # add routine to user
        self.user.routines.append(routine)

        # add routine component to routines_vbox
        self.routine_components.append(RoutineComponent(routine))
