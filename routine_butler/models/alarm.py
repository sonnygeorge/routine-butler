from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from routine_butler.configs import N_SECONDS_BETWEEN_ALARM_CHECKS


class RingFrequency(StrEnum):
    CONSTANT = "constant"
    PERIODIC = "periodic"


class Alarm(BaseModel):
    time: str = "12:00"
    is_enabled: bool = True
    volume: float = 1.0
    ring_frequency: RingFrequency = RingFrequency.CONSTANT

    def get_seconds_until_time(self) -> int:
        """Returns the differential in total seconds between now and the alarm's time."""
        now = datetime.now()
        alarm_time = datetime.strptime(self.time, "%H:%M").time()
        alarm_datetime = datetime.combine(now.date(), alarm_time)
        return int((alarm_datetime - now).total_seconds())

    def should_ring(self) -> bool:
        """Returns True if the alarm should be rung, False otherwise."""
        if not self.is_enabled:
            return False
        seconds_until_alarm = self.get_seconds_until_time()
        return -N_SECONDS_BETWEEN_ALARM_CHECKS < seconds_until_alarm <= 0
