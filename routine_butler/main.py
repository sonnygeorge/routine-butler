from functools import partial

from nicegui import ui, app
from loguru import logger
from sqlmodel import SQLModel

from routine_butler.elements.header import Header
from routine_butler.elements.routines_sidebar import RoutinesSidebar
from routine_butler.elements.programs_sidebar import ProgramsSidebar
from routine_butler.database.models import User
from routine_butler.database.repository import Repository, TEST_USER_USERNAME
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


def main_page(user: User, repository: Repository):
    assert user is not None

    set_colors()

    header = Header()
    routines_sidebar = RoutinesSidebar(user=user, repository=repository)
    programs_sidebar = ProgramsSidebar(user=user, repository=repository)

    header.routines_button.on("click", routines_sidebar.toggle)
    header.programs_button.on("click", programs_sidebar.toggle)


class RoutineButler:
    def __init__(self, repository: Repository, testing: bool = False):
        self.repository = repository
        self.user = None

        if not testing:
            self.login_card()
        else:
            button = ui.button("Log in as test user")
            button.on("click", self.login_as_test_user)

    def login_card(self):
        set_colors()

        with ui.card():
            ui.label("Login")
            ui.separator()
            username_input = ui.input("Username")
            login_button = ui.button("Login")

        login_button.on(
            "click", lambda: self.on_login_attempt(username_input.value)
        )

    def login_as_test_user(self):
        logger.debug("Logging in as test user")
        self.on_login_attempt(TEST_USER_USERNAME)

    def on_login_attempt(self, username):
        user = self.repository.eagerly_get_user(username)

        undecorated_users_page = partial(main_page, user, self.repository)
        users_page = ui.page("/main_page")(undecorated_users_page)

        if user is None:
            ui.notify("Invalid username")
        else:
            self.user = user
            ui.open(users_page)


def main(testing: bool = False):
    def _main(repository: Repository):
        RoutineButler(repository=repository, testing=testing)
        ui.run()

    repository = Repository(testing=testing)

    if testing:
        _main(repository)
        app.on_shutdown(lambda: SQLModel.metadata.drop_all(repository.engine))
    else:
        _main(repository)
