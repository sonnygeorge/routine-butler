from sqlmodel import Session

from routine_butler.model.model import User, Routine, RoutineItem


class TestCRUDMixin:
    def _user(self) -> User:
        return User(routines=[Routine(routine_items=[RoutineItem()])])

    def test_create_in_db(self, session: Session):
        user = self._user()
        user.add_to_db(session)
        assert user.username is not None
        assert user.routines[0].id is not None
        assert user.routines[0].routine_items[0].id is not None

    def test_get_from_db(self, session: Session):
        user = self._user()
        user.add_to_db(session)
        user_from_db = User.get_from_db(session, uid=user.username)
        assert user_from_db == user
        assert user_from_db.routines[0] == user.routines[0]
        assert (
            user_from_db.routines[0].routine_items[0]
            == user.routines[0].routine_items[0]
        )

    def test_update_in_db(self, session: Session):
        routine = Routine()
        routine.add_to_db(session)
        routine.update_in_db(session, title="New and Different Title")
        assert routine.title == "New and Different Title"
        routine_from_db = Routine.get_from_db(session, uid=routine.id)
        assert routine_from_db.title == "New and Different Title"

    def test_update_in_db_with_relationship(self, session: Session):
        routine = Routine()
        routine.add_to_db(session)
        routine_item = RoutineItem()
        routine.update_in_db(
            session, routine_items=routine.routine_items + [routine_item]
        )
        assert routine_item.id is not None  # TODO: finish

    def test_delete_from_db(self, session: Session):
        routine = Routine()
        routine.add_to_db(session)
        routine.delete_from_db(session)
        assert Routine.get_from_db(session, uid=routine.id) is None
