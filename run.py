import argparse

from loguru import logger
from sqlalchemy import create_engine

from routine_butler.main import main
from routine_butler.models.base import SQLAlchemyBase

TEST_DB_URL = "sqlite:///test_db.sqlite"
DB_URL = "sqlite:///db.sqlite"
TEST_USER_USERNAME = "test"


if __name__ in {"__main__", "__mp_main__"}:
    # Define the "--testing" cli argument
    parser = argparse.ArgumentParser(description="Runs RoutineButler")
    help = "If used, the app will run with a test database and auto-login w/ a test user"
    parser.add_argument("--testing", action="store_true", help=help)

    # Parse the arguments
    args = parser.parse_args()

    if args.testing:
        # Create a test database
        engine = create_engine(TEST_DB_URL)
        SQLAlchemyBase.metadata.create_all(engine)

        # Run the app
        main(engine, auto_login=TEST_USER_USERNAME)
    else:
        if __name__ == "__main__":
            logger.info("Running in production mode")
        engine = create_engine(DB_URL)
        SQLAlchemyBase.metadata.create_all(engine)
        main(engine)
