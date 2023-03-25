import remi

from components.header import Header
from components.routines_container import RoutinesContainer
from components.topmost_container import TopmostContainer
from database import database
from models import User


class App(remi.server.App):
    def main(self):
        """Gets called when the app is started"""
        self.user: User = database.get(User, 1)  # test user for development

        # main container
        self.topmost_container = TopmostContainer()

        # header container
        self.header = Header()
        self.topmost_container.append(self.header, "header")

        # routines container
        self.routines_container = RoutinesContainer(self.user)
        self.topmost_container.append(
            self.routines_container, "routines_container"
        )

        return self.topmost_container

    def idle(self):
        """Gets called every update_interval seconds"""
        # header component idle function
        self.header.idle()
        # routine components idle function
        self.routines_container.idle()
        # since all models are children of user, this persists all changes to the db
        database.commit(self.user)


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
