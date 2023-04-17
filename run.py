import argparse
import os

from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, SQLModel, create_engine
from nicegui import app

from routine_butler.main import main
from routine_butler.database import models  # required to create schema
from routine_butler.database.models import User, Program


TEST_DB_URL = "sqlite:///test_db.sqlite"
DB_URL = "sqlite:///db.sqlite"
TEST_USER_USERNAME = "test"


if __name__ in {"__main__", "__mp_main__"}:
    # Define the "--testing" cli argument
    parser = argparse.ArgumentParser(description="Script description")
    help = "If used, the app will be run with a test database w/ a single fake test user"
    parser.add_argument("--testing", action="store_true", help=help)

    # Parse the arguments
    args = parser.parse_args()

    if args.testing:
        # # Delete the test database if it already exists
        # if os.path.exists(TEST_DB_URL.split(":///")[1]):
        #     os.remove(TEST_DB_URL.split(":///")[1])

        # Create a test database
        engine = create_engine(TEST_DB_URL)
        SQLModel.metadata.create_all(engine)

        if __name__ == "__mp_main__":
            logger.info("Running in testing mode")
            # Create a test user
            with Session(engine) as session:
                try:
                    test_user = User(username=TEST_USER_USERNAME)
                    session.add(test_user)

                    # add programs
                    session.add(Program(title="program 1", user=test_user))
                    session.add(Program(title="program 2", user=test_user))
                    session.commit()
                except IntegrityError:
                    # iignore error if user already exists
                    pass

        # # Add deletion of test database metadata to handlers of app shutdown
        # app.on_shutdown(lambda: SQLModel.metadata.drop_all(engine))

        # Run the app
        main(engine, auto_login=TEST_USER_USERNAME)
    else:
        if __name__ == "__main__":
            logger.info("Running in production mode")
        engine = create_engine(DB_URL)
        SQLModel.metadata.create_all(engine)
        main(engine)
