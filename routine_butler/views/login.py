from nicegui import ui

from routine_butler.components.header import Header
from routine_butler.constants import PagePath
from routine_butler.models.user import User
from routine_butler.state import state
from routine_butler.utils import apply_color_theme


@ui.page(path=PagePath.LOGIN)
def login():
    def handle_login_attempt(username: str):
        # query db for user
        is_user_filter_expr = User.Config.orm_model.username == username
        user = User.query_one(state.engine, filter_=is_user_filter_expr)

        if user is None:
            # create new user w/ username
            user = User(username=username)
            user.add_self_to_db(state.engine)

        state.set_user(user)
        ui.open(PagePath.HOME)

    apply_color_theme()
    Header()

    with ui.card():
        ui.label("Login")
        ui.separator()
        username_input = ui.input("User:")
        btn = ui.button("Login")
        btn.on(
            "click",
            lambda: handle_login_attempt(username_input.value),
        )
