from sqlmodel import Session

from .database.models import User, Routine


class RoutineCtl:
    def __init__(self, db_engine, username: str):
        self.db_engine = db_engine
        self.username = username

    def session(self):
        return Session(self.db_engine)

    def get_user(self):
        return User.eagerly_get_user(self.session(), self.username)

    def add_routine(self, session):
        """add routine with placeholder name"""
        routine = Routine(user_username=self.username)
        session.add(routine)
        session.commit()
        return routine

    def rename_routine(self, session, routine_id, new_title):
        routine = session.get(Routine, routine_id)
        routine.title = new_title
        session.add(routine)
        session.commit()
