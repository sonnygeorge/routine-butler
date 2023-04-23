import os

from sqlmodel import create_engine, Session, SQLModel
import pytest

from routine_butler.model import model


TEST_DB_URL = "sqlite:///unit_test_db.sqlite"
TEST_USER_USERNAME = "test"


@pytest.fixture(scope="session")
def engine():
    if os.path.exists(TEST_DB_URL.split(":///")[1]):
        os.remove(TEST_DB_URL.split(":///")[1])
    
    engine = create_engine(TEST_DB_URL, echo=False)
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    _session = Session(bind=connection)
    yield _session
    _session.close()
    transaction.rollback()
    connection.close()
