import argparse

from sqlmodel import SQLModel
from nicegui import app
from loguru import logger

from sqlmodel import Session

from routine_butler.main import main
from routine_butler.database.repository import Repository
from routine_butler.database.models import User


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

        # Create a test database
        repository = Repository()
        repository.create_db(TEST_DB_URL)

        # Create a test user
        test_user = User(username=TEST_USER_USERNAME)

        if __name__ == "__main__":
            logger.info("Running in testing mode")
            # Add to db
            with repository.session() as session:
                session.add(test_user)
                session.commit()
                test_user = repository.eagerly_get_user(
                    username=TEST_USER_USERNAME, session=session
                )

        # Add deletion of test database metadata to handlers of app shutdown
        app.on_shutdown(lambda: SQLModel.metadata.drop_all(repository.engine))

        # Run the app
        main(repository=repository, user=test_user)
    else:
        if __name__ == "__main__":
            logger.info("Running in production mode")
        repository = Repository()
        repository.create_db(DB_URL)
        main(repository=repository)
