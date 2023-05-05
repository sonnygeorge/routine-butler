import pytest
from sqlalchemy.engine import Engine

from routine_butler.models.base import InstanceAlreadyExistsError
from routine_butler.models.routine import Routine
from routine_butler.models.user import User

TEST_USER_USERNAME = "test_user"


@pytest.fixture(scope="module")
def user(engine: Engine) -> User:
    user = User(username=TEST_USER_USERNAME)
    user.add_self_to_db(engine)
    yield user
    user.delete_self_from_db(engine)


@pytest.mark.xfail(InstanceAlreadyExistsError)
def test_add_user_with_same_username(engine: Engine, user: User):
    # NOTE: a user w TEST_USER_USERNAME was already added to db by the fixture
    user2 = User(username=TEST_USER_USERNAME)
    user2.add_self_to_db(engine)


def test_get_routines_empty(engine: Engine, user: User):
    assert user.get_routines(engine) == []


def test_get_programs_empty(engine: Engine, user: User):
    assert user.get_programs(engine) == []


def test_basic_add_routine(engine: Engine, user: User):
    routine = Routine()
    user.add_routine(engine, routine)
    assert routine.uid is not None


def test_basic_add_program(engine: Engine, user: User):
    pass  # TODO


def test_basic_get_routines(engine: Engine, user: User):
    routine = Routine()
    user.add_routine(engine, routine)
    assert routine in user.get_routines(engine)


def test_basic_get_programs(engine: Engine, user: User):
    pass  # TODO
