import remi
from loguru import logger

from components.primitives.button import Button
from components.routine_component import RoutineComponent
from models import Routine, User


class RoutinesContainer(remi.gui.VBox):
    """VBox-style container for the routine components of the app/user."""

    user: User
    routine_component_directory: list[RoutineComponent] = []

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
                "margin": "23px 23px 23px 23px",
                "background": "none",
                "justify-content": "space-between",
            },
        )
        self.routines_vbox.css_background_color = "transparent"
        self.append(self.routines_vbox, "routines_vbox")

        self.populate_routine_component_directory()
        self.conduct_screen_management()

        # add routine button
        self.add_routine_button = Button(
            "+", style={"margin": "12px", "font-size": "30px"}
        )
        self.add_routine_button.css_width = "9%"
        self.add_routine_button.onclick.connect(self.on_add_routine)
        self.append(self.add_routine_button, "add_routine_button")

    def populate_routine_component_directory(self):
        """Instantiates the routines from user's routines"""
        for routine in self.user.routines:
            self.routine_component_directory.append(
                RoutineComponent(routine, self.user)
            )

    def on_add_routine(self, _):
        """Called when the user clicks on the add_routine_button."""
        logger.debug("Adding new routine")
        # create new routine
        routine = Routine()
        # add routine to user
        self.user.routines.append(routine)
        # add routine component to routines_vbox
        routine_component = RoutineComponent(routine, self.user)
        self.routine_component_directory.append(routine_component)
        self.routines_vbox.append(routine_component, key=routine.id)

    def idle(self):
        """Called every update_interval seconds."""
        self.conduct_screen_management()
        for routine_component in self.routine_component_directory:
            routine_component.idle()

    def conduct_screen_management(self):
        """
        Iterates through all routine components and "manages the stage" by either:
            1. Adding a routine component to the screen
            2. Hiding a routine component from the screen
            3. Deleting a routine component and object altogether
        """
        on_screen = lambda r: r in self.routines_vbox.children.values()

        for routine_comp in self.routine_component_directory:
            if routine_comp.trashed:
                self.delete_routine_altogether(routine_comp)
            elif routine_comp.should_be_on_screen() and not on_screen(
                routine_comp
            ):
                self.add_routine_to_screen(routine_comp)
            elif (
                on_screen(routine_comp)
                and not routine_comp.should_be_on_screen()
            ):
                self.hide_routine_from_screen(routine_comp)

    def delete_routine_altogether(self, routine_component: RoutineComponent):
        """Thoroughly deletes a routine object from the app and database"""
        # remove from screen
        self.routines_vbox.remove_child(routine_component)
        # remove from class list
        self.routine_component_directory.remove(routine_component)
        # remove from user
        self.user.routines.remove(routine_component.routine)

    def add_routine_to_screen(self, routine_component):
        """Adds a routine to the screen"""
        # add to screen
        self.routines_vbox.append(
            routine_component, key=routine_component.routine.id
        )
        # add to directory if not already there
        if routine_component not in self.routine_component_directory:
            self.routine_component_directory.append(routine_component)

    def hide_routine_from_screen(self, routine_component):
        """Temporarily removes a routine from the screen"""
        self.routines_vbox.remove_child(routine_component)
