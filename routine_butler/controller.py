from sqlmodel import Session
from loguru import logger

from .model.model import User, Routine, RoutineItem, Program


CTL_LOG_LEVEL = "CONTROLLER"
logger.level(CTL_LOG_LEVEL, no=33, color="<yellow>")


class RoutineCtl:
    def __init__(self, db_engine, username: str):
        self.db_engine = db_engine
        self.username = username

    def session(self):
        return Session(self.db_engine)

    def get_user(self, session: Session):
        logger.log(CTL_LOG_LEVEL, "Getting user")
        return User.get_from_db(session, self.username)

    def add_routine(self, session: Session):
        """adds a default instance of a routine"""
        logger.log(CTL_LOG_LEVEL, "Adding routine")
        routine = Routine(user_username=self.username)
        session.add(routine)
        session.commit()
        return routine

    def delete_routine(self, session: Session, routine_id: int):
        logger.log(CTL_LOG_LEVEL, "Deleting routine")
        routine = session.get(Routine, routine_id)
        session.delete(routine)
        session.commit()

    def update_routine_title(
        self, session: Session, routine_id: int, new_title: str
    ):
        logger.log(CTL_LOG_LEVEL, f"Updating routine title to {new_title}")
        routine = session.get(Routine, routine_id)
        routine.title = new_title
        session.add(routine)
        session.commit()

    def update_target_duration(
        self, session: Session, routine_id: int, new_val: int
    ):
        logger.log(
            CTL_LOG_LEVEL, f"Updating routine target_duration to {new_val}"
        )
        routine = session.get(Routine, routine_id)
        routine.target_duration = new_val
        session.add(routine)
        session.commit()

    def update_target_duration_enabled(
        self, session: Session, routine_id: int, new_val: int
    ):
        logger.log(
            CTL_LOG_LEVEL,
            f"Updating routine target_duration_enabled to {new_val}",
        )
        routine = session.get(Routine, routine_id)
        routine.target_duration_enabled = new_val
        session.add(routine)
        session.commit()


class RoutineItemCtl:
    def __init__(self, routine_ctl: RoutineCtl, routine_id: int):
        self.db_engine = routine_ctl.db_engine
        self.get_user = routine_ctl.get_user
        self.routine_id = routine_id
        self.last_reg_idx = -1

    def _update_last_reg_index(self, routine: Routine):
        """updates the last_reg_index attribute of the controller"""
        if not routine.routine_items:
            self.last_reg_idx = -1
        else:
            is_reg = [not ri.is_reward for ri in routine.routine_items]
            self.last_reg_idx = sum(is_reg) - 1

    def session(self):
        return Session(self.db_engine)

    def get_routine(self, session: Session):
        logger.log(CTL_LOG_LEVEL, "Getting routine")
        return Routine.get_routine(session, self.routine_id)

    def add_routine_item(self, session: Session):
        """adds a default instance of a routine item"""
        logger.log(CTL_LOG_LEVEL, "Adding routine item")
        routine = session.get(Routine, self.routine_id)
        if self.last_reg_idx is None:
            self._update_last_reg_index(routine)
        # create routine item to routine object with order index of the last_reg_idx + 1
        routine_item = RoutineItem(
            order_index=self.last_reg_idx + 1, routine=routine
        )
        session.add(routine_item)
        # update last_reg_idx
        self.last_reg_idx += 1
        # update order index of all routine items after the new routine item
        for ri in routine.routine_items:
            if ri.order_index > self.last_reg_idx:
                ri.order_index += 1
                session.add(ri)
        session.commit()
        return routine_item
