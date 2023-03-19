from dataclasses import dataclass

@dataclass
class Schedule:
    hour = 0
    minute = 0
    is_active = False