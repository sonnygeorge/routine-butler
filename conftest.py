import os

from sqlmodel import Session, SQLModel
import pytest

from routine_butler.database import models
from routine_butler.database.repository import Repository


TEST_DB_URL = "sqlite:///test_db.sqlite"
TEST_USER_USERNAME = "test"


@pytest.fixture(scope="session")
def repository():
    repository = Repository()
    # Delete the test database if it already exists
    if os.path.exists(TEST_DB_URL.split(":///")[1]):
        os.remove(TEST_DB_URL.split(":///")[1])
    # Create the test database
    repository.create_db(url=TEST_DB_URL)
    # Create a test user
    with repository.session() as session:
        test_user = models.User(username=TEST_USER_USERNAME)
        session.add(test_user)
        session.commit()
    # Set the repository current_username attribute
    repository.current_username = TEST_USER_USERNAME

    yield repository

    SQLModel.metadata.drop_all(repository.engine)


@pytest.fixture(scope="function")
def session(repository: Repository):
    connection = repository.engine.connect()
    transaction = connection.begin()
    _session = Session(bind=connection)
    yield _session
    _session.close()
    transaction.rollback()
    connection.close()
