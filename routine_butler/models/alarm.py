import datetime
from enum import StrEnum

from pydantic import BaseModel

from routine_butler.configs import N_SECONDS_BW_RING_CHECKS


class RingFrequency(StrEnum):
    CONSTANT = "constant"
    PERIODIC = "periodic"


class Alarm(BaseModel):
    time_str: str = "12:00"
    is_enabled: bool = True
    volume: float = 1.0
    ring_frequency: RingFrequency = RingFrequency.CONSTANT

    @property
    def _time(self) -> datetime.time:
        return datetime.datetime.strptime(self.time_str, "%H:%M").time()

    def get_todays_ring_datetime(self) -> datetime.datetime:
        todays_date = datetime.datetime.now().date()
        return datetime.datetime.combine(todays_date, self._time)

    def has_just_passed_as_of_last_ring_check(self):
        """Returns True if the alarm has just passed as of the last ring check, False
        otherwise."""
        secs_until_todays_ring_dtime = (
            self.get_todays_ring_datetime() - datetime.datetime.now()
        ).total_seconds()
        return -N_SECONDS_BW_RING_CHECKS <= secs_until_todays_ring_dtime <= 0

    def should_ring(self) -> bool:
        """Returns True if the alarm should be rung, False otherwise."""
        return self.is_enabled and self.has_just_passed_as_of_last_ring_check()

    def get_next_ring_datetime(self) -> datetime.datetime:
        """Returns the datetime of the next time the alarm should be rung."""
        now = datetime.datetime.now()
        todays_ring_dtime = self.get_todays_ring_datetime()
        if todays_ring_dtime < now:  # is past, then next is tomorrow
            return todays_ring_dtime.replace(day=now.day + 1)
        else:  # next is today
            return todays_ring_dtime
