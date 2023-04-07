from sqlmodel import Session, SQLModel
import pytest

from routine_butler.database import models
from routine_butler.database.repository import Repository


TEST_DB_URL = "sqlite:///test_db.sqlite"


@pytest.fixture(scope="session")
def repository():
    repository = Repository()
    repository.create_db(url=TEST_DB_URL)
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
