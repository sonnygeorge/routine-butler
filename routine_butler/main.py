from functools import partial
from typing import Optional

from nicegui import ui, app
from loguru import logger
from sqlmodel import SQLModel

from routine_butler.elements.header import Header
from routine_butler.elements.routines_sidebar import RoutinesSidebar
from routine_butler.elements.programs_sidebar import ProgramsSidebar
from routine_butler.database.models import User
from routine_butler.database.repository import Repository
from routine_butler.utils.constants import clrs


def set_colors():
    ui.colors(
        primary=clrs.primary,
        secondary=clrs.secondary,
        accent=clrs.accent,
        positive=clrs.positive,
        negative=clrs.negative,
        info=clrs.info,
        warning=clrs.warning,
    )


class RoutineButler:
    def __init__(self, repository: Repository, user: Optional[User] = None):
        self.repository = repository
        self.user = user
        logger.debug(self.user)
        self.main_frame = ui.element("div")

        if user is None:
            with self.main_frame:
                self.login()
        else:
            # set repository current_username attribute
            self.repository.current_username = user.username
            # instantiate main gui without login
            with self.main_frame:
                self.main_gui()

    def login(self):
        set_colors()

        with ui.card():
            ui.label("Login")
            ui.separator()
            username_input = ui.input("Username")
            login_button = ui.button("Login")

        login_button.on(
            "click", lambda: self.on_login_attempt(username_input.value)
        )

    def main_gui(self):
        assert self.user is not None

        set_colors()

        header = Header()
        routines_sidebar = RoutinesSidebar(
            user=self.user, repository=self.repository
        )
        programs_sidebar = ProgramsSidebar(
            user=self.user, repository=self.repository
        )

        header.routines_button.on("click", routines_sidebar.toggle)
        header.programs_button.on("click", programs_sidebar.toggle)

    def on_login_attempt(self, username):
        with self.repository.session() as session:
            user = self.repository.eagerly_get_user(username, session=session)

        if user is None:
            ui.notify("Invalid username")
        else:
            self.user = user
            self.repository.current_username = user.username
            self.main_frame.clear()
            with self.main_frame:
                self.main_gui()
            ui.notify("Welcome, " + user.username + "!")


def main(repository: Repository, user: Optional[User] = None):
    RoutineButler(repository, user)
    ui.run()
