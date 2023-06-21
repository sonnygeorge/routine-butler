from nicegui import ui

from routine_butler.components import micro
from routine_butler.configs import PagePath
from routine_butler.models import User
from routine_butler.state import state
from routine_butler.utils import initialize_page


@ui.page(path=PagePath.LOGIN)
def login():
    def hdl_login_attempt(username: str):
        # query db for user
        is_user_filter_expr = User.Config.orm_model.username == username
        user = User.query_one(state.engine, filter_=is_user_filter_expr)

        if user is None:
            # create new user w/ the given username
            user = User(username=username)
            user.add_self_to_db(state.engine)

        state.set_user(user)
        ui.open(PagePath.HOME)

    initialize_page(page=PagePath.LOGIN, state=state)

    with micro.card() as base:
        base.classes("max-w-xl absolute-center container flex items-stretch")

        ui.label("Login")
        ui.separator()
        username_input = micro.input("User")
        btn = ui.button("Login")
        btn.on(
            "click",
            lambda: hdl_login_attempt(username_input.value),
        )
