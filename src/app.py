import remi

from components.header import Header
from components.topmost_container import TopmostContainer
from components.body_container import BodyContainer
from typing import List

from components.routine import Routine
from database import UserModel, Database


class App(remi.server.App):
    user: UserModel = Database().get(UserModel, 1)  # TEMP: default user for development
    routines: List[Routine] = []

    def main(self):
        """Gets called when the app is started"""
        # main container
        self.topmost_container = TopmostContainer()

        # header containerD
        self.header = Header()
        self.topmost_container.append(self.header, "header")

        # body container
        self.body_container = BodyContainer()
        self.topmost_container.append(self.body_container, "body")

        self.instantiate_routines()
        self.update_content()
        return self.topmost_container

    def idle(self):
        """Gets called every update_interval seconds"""
        self.header.update()
        self.update_content()
        # since all models are children of the user, this persists all changes to the db
        Database().update(self.user)

    def instantiate_routines(self):
        """Instantiates the routines from user's configurations"""
        for routine_data in self.user.routines:
            self.routines.append(Routine(routine_data))

    def update_content(self):
        """Updates the content of the app"""
        for routine in self.routines:
            routine_id = routine.routine_model.id
            # if routine should be on stage and is not already on stage
            if (
                routine.should_be_on_screen()
                and routine not in self.body_container.children.values()
            ):
                self.body_container.append(routine, routine_id)
                routine.update()
            # if routine should not be on stage and is already on stage
            elif (
                not routine.should_be_on_screen()
                and routine in self.body_container.children.values()
            ):
                self.body_container.remove_child(routine)
            # if routine should be on stage and is already on stage
            else:
                routine.update()


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
