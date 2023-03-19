from dataclasses import dataclass

from schema.schedule import Schedule


@dataclass
class RoutineConfigurations:
    routine_id: str = "default_routine"
    schedule: Schedule = Schedule()
