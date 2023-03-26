import remi

from components.header import Header
from components.routines_frame.routines_frame import RoutinesFrame
from database import database
from models import User


class App(remi.server.App):
    def main(self):
        """Gets called when the app is started"""
        self.user: User = database.get(User, 1)  # test user for development

        # main container
        self.topmost_frame = remi.gui.Container()
        self.topmost_frame.css_width = "100%"
        self.topmost_frame.css_height = "100%"
        self.topmost_frame.css_background_color = "lightgray"
        self.topmost_frame.css_font_family = "Courier"

        # header container
        self.header = Header()
        self.topmost_frame.append(self.header, "header")

        # routines frame
        self.routines_frame = RoutinesFrame(self.user)
        self.topmost_frame.append(self.routines_frame, "routines_frame")

        return self.topmost_frame

    def idle(self):
        """Gets called every update_interval seconds"""
        # header component idle function
        self.header.idle()
        # routine components idle function
        self.routines_frame.idle()
        # since all models are children of user, this persists all changes to the db
        database.commit(self.user)


if __name__ == "__main__":
    remi.start(
        App,
        address="0.0.0.0",
        port=8080,
        start_browser=False,
        username=None,
        password=None,
        update_interval=1,
    )
