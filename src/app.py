from typing import List

import remi

from components.body_container import BodyContainer
from components.header import Header
from components.routine_component import RoutineComponent
from components.topmost_container import TopmostContainer
from database import database
from models import User


class App(remi.server.App):
    user: User = database.get(User, 1)  # TEMP: test user for development
    routine_components: List[RoutineComponent] = []

    def main(self):
        """Gets called when the app is started"""
        # main container
        self.topmost_container = TopmostContainer()

        # header container
        self.header = Header()
        self.topmost_container.append(self.header, "header")

        # body container
        self.body_container = BodyContainer()
        self.topmost_container.append(self.body_container, "body")

        self.instantiate_routine_components()
        self.manage_body_components_and_run_idle_funcs()
        return self.topmost_container

    def instantiate_routine_components(self):
        """Instantiates the routines from user's routines"""
        for routine in self.user.routines:
            self.routine_components.append(RoutineComponent(routine))

    def idle(self):
        """Gets called every update_interval seconds"""
        # header component idle function
        self.header.idle()
        # add/remove body components and run their idle functions
        self.manage_body_components_and_run_idle_funcs()
        # since all models are children of user, this persists all changes to the db
        database.commit(self.user)

    def manage_body_components_and_run_idle_funcs(self):
        """Adds/removes body components and runs their idle functions"""
        for routine_component in self.routine_components:
            # if routine component should be on the screen and is not already
            if (
                routine_component.should_be_on_screen()
                and routine_component
                not in self.body_container.children.values()
            ):
                self.body_container.append(
                    routine_component, key=routine_component.routine.id
                )
                routine_component.idle()

            # if routine component should not be on the screen and is already
            elif (
                not routine_component.should_be_on_screen()
                and routine_component in self.body_container.children.values()
            ):
                self.body_container.remove_child(routine_component)
            # if routine component should be on the screen and is already
            else:
                routine_component.idle()


if __name__ == "__main__":
    remi.start(
        App,
        address="0.0.0.0",
        port=0,
        start_browser=True,
        username=None,
        password=None,
        update_interval=1,
    )
