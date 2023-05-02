import time

import pytest
from pydantic import ValidationError, constr
from sqlalchemy import Column, String
from sqlalchemy.engine.base import Engine

from routine_butler.models.base import (
    AttemptedSetOnReadOnlyFieldError,
    BaseDBORMModel,
    BaseDBPydanticModel,
    DatabaseDeletionFailedError,
    DatabaseUpdateFailedError,
    InstanceAlreadyExistsError,
)

INTEGRATION_TEST_DB_FPATH = "test_database.db"


class HeroORM(BaseDBORMModel):
    """Arbitrary BaseDBORMModel model for testing purposes"""

    __tablename__ = "heros"

    NAME_LENGTH_LIMIT = 60

    name = Column(String(NAME_LENGTH_LIMIT))


class Hero(BaseDBPydanticModel):
    """Arbitrary BaseDBPydanticModel model for testing purposes"""

    name: constr(max_length=HeroORM.NAME_LENGTH_LIMIT) = "Superman"

    class Config:
        orm_model = HeroORM


# BaseDBPydanticModel.__init__()


@pytest.mark.xfail(raises=ValidationError)
def test_create_invalid():
    Hero(name="a" * (HeroORM.NAME_LENGTH_LIMIT + 1))


@pytest.mark.xfail(raises=AttemptedSetOnReadOnlyFieldError)
@pytest.mark.parametrize("field_name", BaseDBPydanticModel._READ_ONLY_FIELDS)
def test_initialize_read_only_field(field_name):
    Hero(**{field_name: "something"})


# BaseDBPydanticModel.__setattr__()


@pytest.mark.xfail(raises=AttemptedSetOnReadOnlyFieldError)
@pytest.mark.parametrize("field_name", BaseDBPydanticModel._READ_ONLY_FIELDS)
def test_modify_read_only_field(field_name):
    hero = Hero()
    setattr(hero, field_name, "something else")


# BaseDBPydanticModel._validate_orm_model()


@pytest.mark.xfail(raises=NotImplementedError)
def test_no_orm_model():
    class ForgotToAddOrmModel(BaseDBPydanticModel):
        pass

    ForgotToAddOrmModel._validate_orm_model()


@pytest.mark.xfail(raises=TypeError)
def test_invalid_orm_model():
    class InvalidOrmModel(BaseDBPydanticModel):
        class Config:
            orm_model = "not a valid orm model"

    InvalidOrmModel._validate_orm_model()


# BaseDBPydanticModel.add_self_to_db()


def test_basic_add_self_to_db(engine: Engine):
    hero = Hero()
    hero.add_self_to_db(engine)
    assert hero.uid is not None
    assert hero.created_at is not None and hero.updated_at is not None
    # make sure updated_at and created_at are (virtually) the same
    assert abs((hero.updated_at - hero.created_at).total_seconds()) < 0.0001


@pytest.mark.xfail(raises=InstanceAlreadyExistsError)
def test_add_duplicate(engine: Engine):
    hero = Hero()
    hero.add_self_to_db(engine)
    hero.add_self_to_db(engine)


# BaseDBPydanticModel.update_self_in_db()


def test_basic_update_self_in_db(engine: Engine):
    hero = Hero()
    hero.add_self_to_db(engine)
    time.sleep(0.1)
    hero.name = "Batman"
    hero.update_self_in_db(engine)
    # make sure > 0.1 seconds between created_at and updated_at
    assert hero.created_at is not None and hero.updated_at is not None
    assert (hero.updated_at - hero.created_at).total_seconds() > 0.1
    # make sure database returns the same data
    same_id_filter_exp = Hero.Config.orm_model.uid == hero.uid
    assert hero.query_one(engine, filter_=same_id_filter_exp) == hero


@pytest.mark.xfail(raises=DatabaseUpdateFailedError)
def test_update_self_non_existent(engine: Engine):
    hero = Hero()
    hero.update_self_in_db(engine)


# BaseDBPydanticModel.query_one()


def test_basic_query_one(engine: Engine):
    hero = Hero()
    hero.add_self_to_db(engine)
    same_id_filter_exp = Hero.Config.orm_model.uid == hero.uid
    assert hero.query_one(engine, filter_=same_id_filter_exp) == hero


def test_query_one_non_existent(engine: Engine):
    impossible_uid = -1
    impossible_uid_filter_exp = Hero.Config.orm_model.uid == impossible_uid
    assert Hero.query_one(engine, filter_=impossible_uid_filter_exp) is None


def test_query_one_multiple_matches(engine: Engine):
    hero1 = Hero()
    hero1.add_self_to_db(engine)
    hero2 = Hero()
    hero2.add_self_to_db(engine)
    same_ids_filter_exp = Hero.Config.orm_model.uid.in_([hero1.uid, hero2.uid])
    with pytest.warns():
        Hero.query_one(engine, filter_=same_ids_filter_exp)


# BaseDBPydanticModel.query_many()


def test_basic_query_many(engine: Engine):
    hero1 = Hero()
    hero1.add_self_to_db(engine)
    hero2 = Hero()
    hero2.add_self_to_db(engine)
    same_ids_filter_exp = Hero.Config.orm_model.uid.in_([hero1.uid, hero2.uid])
    qry_result = Hero.query_many(engine, filter_=same_ids_filter_exp)
    assert qry_result == [hero1, hero2]


def test_basic_query_many_no_filter(engine: Engine):
    hero1 = Hero()
    hero1.add_self_to_db(engine)  # make sure something in db table
    qry_result = Hero.query_many(engine, limit=3)
    assert len(qry_result) > 0  # make sure something (anything) is returned


def test_query_many_no_matches(engine: Engine):
    impossible_uid = -1
    impossible_uid_filter_exp = Hero.Config.orm_model.uid == impossible_uid
    assert Hero.query_many(engine, filter_=impossible_uid_filter_exp) == []


def test_query_many_order_by(engine: Engine):
    names = ["Superman", "Green Lantern", "Batman"]
    uids = []
    for name in names:
        hero = Hero(name=name)
        hero.add_self_to_db(engine)
        uids.append(hero.uid)
    same_ids_filter_exp = Hero.Config.orm_model.uid.in_(uids)
    name_asc_order_by_exp = Hero.Config.orm_model.name.asc()
    qry_result = Hero.query_many(
        engine, filter_=same_ids_filter_exp, order_by=name_asc_order_by_exp
    )
    assert [hero.name for hero in qry_result] == sorted(names)


# BaseDBPydanticModel.delete_self_from_db()


def test_basic_delete_self_from_db(engine: Engine):
    hero = Hero()
    hero.add_self_to_db(engine)
    id_before_delete = hero.uid
    hero.delete_self_from_db(engine)
    same_id_filter_exp = Hero.Config.orm_model.uid == id_before_delete
    assert hero.query_one(engine, filter_=same_id_filter_exp) is None
    assert hero.uid is None
    assert hero.created_at is None and hero.updated_at is None


@pytest.mark.xfail(raises=DatabaseDeletionFailedError)
def test_delete_self_non_existent(engine: Engine):
    hero = Hero()
    hero.delete_self_from_db(engine)


if __name__ == "__main__":
    pytest.main([__file__, "-rx"])
