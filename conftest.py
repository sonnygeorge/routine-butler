import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine

from routine_butler.models.base import SQLAlchemyBase


INTEGRATION_TEST_DB_FPATH = "unit_test_db.sqlite"


@pytest.fixture(scope="session")
def engine() -> Engine:
    engine = create_engine(f"sqlite:///{INTEGRATION_TEST_DB_FPATH}")
    SQLAlchemyBase.metadata.create_all(engine)
    yield engine
    os.remove(INTEGRATION_TEST_DB_FPATH)
