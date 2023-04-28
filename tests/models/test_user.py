from sqlalchemy.engine import Engine

from routine_butler.models.routine import (
    Routine,
    RoutineElement,
    RoutineReward,
    PriorityLevel,
)
from routine_butler.models.user import User


def test_nothing_specific_yet(engine: Engine):  # FIXME
    user = User(username="test")

    routine = Routine()

    user.add_routine(engine, routine)

    print(user.get_routines(engine))

    rou_e = RoutineElement(priority_level=PriorityLevel.LOW, program="test")
    routine.elements.append(rou_e)

    rew_e = RoutineReward(program="test")
    routine.rewards.append(rew_e)

    routine.update_self_in_db(engine)

    print(user.get_routines(engine))
