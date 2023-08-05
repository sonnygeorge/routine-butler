import datetime
from enum import StrEnum

from pydantic import BaseModel

from routine_butler.globals import N_SECONDS_BW_RING_CHECKS


class RingFrequency(StrEnum):
    CONSTANT = "constant"
    PERIODIC = "periodic"


class Alarm(BaseModel):
    time_str: str = "12:00"
    is_enabled: bool = True
    volume: float = 1.0
    ring_frequency: RingFrequency = RingFrequency.CONSTANT

    def __str__(self):
        """Custom __str__ method for logging."""
        return (
            f"[{self.time_str}, {'enabled' if self.is_enabled else 'disabled'}"
            f", vol={self.volume}, ring={self.ring_frequency}]"
        )

    @property
    def _time(self) -> datetime.time:
        return datetime.datetime.strptime(self.time_str, "%H:%M").time()

    def get_todays_ring_datetime(self) -> datetime.datetime:
        todays_date = datetime.datetime.now().date()
        return datetime.datetime.combine(todays_date, self._time)

    def has_just_passed_as_of_last_ring_check(self):
        """Returns True if the alarm has just passed as of the last ring check, False
        otherwise."""
        secs_since_todays_ring_dtime = (
            datetime.datetime.now() - self.get_todays_ring_datetime()
        ).total_seconds()
        return 0 <= secs_since_todays_ring_dtime <= N_SECONDS_BW_RING_CHECKS

    def has_passed_in_the_last_n_minutes(self, n_minutes: int) -> bool:
        """Returns True if the alarm has passed in the last n minutes, False
        otherwise."""
        secs_since_todays_ring_dtime = (
            datetime.datetime.now() - self.get_todays_ring_datetime()
        ).total_seconds()
        return 0 <= secs_since_todays_ring_dtime <= n_minutes * 60

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
