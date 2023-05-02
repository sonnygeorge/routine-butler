from typing import Optional

from nicegui import ui
from sqlalchemy.engine import Engine

from routine_butler.models.user import User
from routine_butler.ui.constants import CLR_CODES
from routine_butler.ui.header import Header
from routine_butler.ui.routines_sidebar import routines_sidebar


def set_colors():
    ui.colors(
        primary=CLR_CODES.primary,
        secondary=CLR_CODES.secondary,
        accent=CLR_CODES.accent,
        positive=CLR_CODES.positive,
        negative=CLR_CODES.negative,
        info=CLR_CODES.info,
        warning=CLR_CODES.warning,
    )


class MainApp:
    def __init__(self, engine: Engine, auto_login: Optional[str] = None):
        self.engine = engine
        self.header = Header()
        self.main_frame = ui.element("div")

        set_colors()

        if auto_login is not None:
            self.handle_login_attempt(username=auto_login)
        else:
            self.login_gui()

    def login_gui(self):
        with self.main_frame:
            with ui.card():
                ui.label("Login")
                ui.separator()
                username_input = ui.input("Username")
                ui.button(
                    "Login",
                    on_click=lambda: self.handle_login_attempt(
                        username_input.value
                    ),
                )

    def main_gui(self, user):
        routines_sidebar_ = routines_sidebar(self.engine, user)
        self.header.routines_button.on("click", routines_sidebar_.toggle)

    def handle_login_attempt(self, username: str):
        is_user_filter_expr = User.Config.orm_model.username == username
        user = User.query_one(self.engine, filter_=is_user_filter_expr)

        if user is None:
            user = User(username=username)
            user.add_self_to_db(self.engine)
            self.main_frame.clear()
            ui.notify("Welcome, new user:" + username + "!")
            self.main_gui(user)
        else:
            self.main_frame.clear()
            ui.notify("Welcome back, " + username + "!")
            self.main_gui(user)


def main(engine: Engine, auto_login: Optional[str] = None):
    MainApp(engine, auto_login)
    ui.run()
