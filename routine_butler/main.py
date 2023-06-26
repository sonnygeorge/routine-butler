from nicegui import ui
from sqlalchemy import create_engine

from routine_butler.configs import DB_URL, TEST_DB_URL, TEST_USER_USERNAME
from routine_butler.models.base import SQLAlchemyBase
from routine_butler.models.user import User
from routine_butler.state import state

# import all views so they are registered with nicegui
from routine_butler.views import *  # noqa: F401, F403


def initialize_db(testing: bool = False) -> None:
    db_url = TEST_DB_URL if testing else DB_URL
    state.engine = create_engine(db_url)
    SQLAlchemyBase.metadata.create_all(state.engine)


def login_test_user() -> None:
    # check if test user already exists in DB
    is_test_user_filter_expr = (
        User.Config.orm_model.username == TEST_USER_USERNAME
    )
    test_user = User.query_one(state.engine, is_test_user_filter_expr)
    if test_user is None:
        # create test user if not
        test_user = User(username=TEST_USER_USERNAME)
        test_user.add_self_to_db(state.engine)
    state.set_user(test_user)  # set current user to test user


def main(testing: bool, fullscreen: bool, native: bool):
    """Main entrypoint for the app."""

    initialize_db(testing=testing)
    if testing:
        login_test_user()

    ui.run(favicon="🚀", native=native, fullscreen=fullscreen)
