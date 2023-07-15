from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel

from routine_butler.configs import N_SECONDS_BW_RING_CHECKS


class RingFrequency(StrEnum):
    CONSTANT = "constant"
    PERIODIC = "periodic"


class Alarm(BaseModel):
    time: str = "12:00"
    is_enabled: bool = True
    volume: float = 1.0
    ring_frequency: RingFrequency = RingFrequency.CONSTANT

    def get_next_ring_datetime(self) -> datetime:
        """Returns the datetime of the next time the alarm should be rung."""
        now = datetime.now()
        alarm_time = datetime.strptime(self.time, "%H:%M").time()
        alarm_datetime = datetime.combine(now.date(), alarm_time)
        if alarm_datetime < now:
            alarm_datetime = alarm_datetime.replace(day=now.day + 1)
        return alarm_datetime

    def should_ring(self) -> bool:
        """Returns True if the alarm should be rung, False otherwise."""
        if not self.is_enabled:
            return False
        timedelta_until_alarm = self.get_next_ring_datetime() - datetime.now()
        seconds_until_alarm = timedelta_until_alarm.total_seconds()
        # should ring if remaining time within ring window
        grace_period = 0.5 * N_SECONDS_BW_RING_CHECKS
        ring_window = N_SECONDS_BW_RING_CHECKS + grace_period
        return seconds_until_alarm <= ring_window
