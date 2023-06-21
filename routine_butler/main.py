from nicegui import ui
from sqlalchemy import create_engine

from routine_butler.models import User
from routine_butler.models.base import SQLAlchemyBase
from routine_butler.state import state

# import views
from routine_butler.views import *  # noqa: F401, F403

TEST_DB_URL = "sqlite:///test_db.sqlite"
DB_URL = "sqlite:///db.sqlite"
TEST_USER_USERNAME = "test"


def main(testing: bool, fullscreen: bool, native: bool):
    db_url = TEST_DB_URL if testing else DB_URL
    state.engine = create_engine(db_url)
    SQLAlchemyBase.metadata.create_all(state.engine)

    if testing:  # automatically log in test user
        # create test user if it doesn't exist
        is_test_user_filter_expr = (
            User.Config.orm_model.username == TEST_USER_USERNAME
        )
        test_user = User.query_one(state.engine, is_test_user_filter_expr)
        if test_user is None:
            test_user = User(username=TEST_USER_USERNAME)
            test_user.add_self_to_db(state.engine)
        # set current user to test user
        state.set_user(test_user)

    ui.run(favicon="🚀", native=native, fullscreen=fullscreen)
