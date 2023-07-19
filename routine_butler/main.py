from nicegui import ui
from sqlalchemy import create_engine

from routine_butler.configs import (
    BINDING_REFRESH_INTERVAL_SECONDS,
    DB_URL,
    SINGLE_USER_MODE_USERNAME,
    TEST_DB_URL,
    TEST_USER_USERNAME,
)
from routine_butler.models.base import SQLAlchemyBase
from routine_butler.models.user import User
from routine_butler.state import state

# import all views so they are registered with nicegui
from routine_butler.views import *  # noqa: F401, F403


def initialize_db(testing: bool = False) -> None:
    db_url = TEST_DB_URL if testing else DB_URL
    state.set_engine(create_engine(db_url))
    SQLAlchemyBase.metadata.create_all(state.engine)


def auto_login_username(username: str) -> None:
    # check if user already exists in DB
    is_user_filter_expr = User.Config.orm_model.username == username
    user = User.query_one(state.engine, is_user_filter_expr)
    if user is None:
        # create user if not
        user = User(username=username)
        user.add_self_to_db(state.engine)
    state.set_user(user)  # set current user to user


def main(
    testing: bool,
    single_user: bool,
    native: bool,
    fullscreen: bool,
    open_browser: bool,
):
    """Main entrypoint for the app."""

    if fullscreen and not native:
        raise ValueError("'fullscreen' doesn't apply outside of 'native' mode")
    if single_user and testing:
        raise ValueError("both 'single_user' & 'testing' args can't be true")
    if native and open_browser:
        raise ValueError("'open_browser' doesn't apply in 'native' mode")

    initialize_db(testing=testing)

    if testing:
        auto_login_username(TEST_USER_USERNAME)
    if single_user:
        auto_login_username(SINGLE_USER_MODE_USERNAME)

    ui.run(
        favicon="🎩",
        native=native,
        fullscreen=fullscreen,
        binding_refresh_interval=BINDING_REFRESH_INTERVAL_SECONDS,
        show=open_browser,
    )
