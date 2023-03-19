from typing import List

from schema.routine_configurations import RoutineConfigurations


class User:
    user_id: str = "default_user"
    routine_configurations: List[RoutineConfigurations] = [RoutineConfigurations()]
