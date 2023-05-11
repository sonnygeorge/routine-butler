from sqlalchemy.engine import Engine

from routine_butler.models.user import User


class State:
    user: User = None
    engine: Engine = None


state = State()
