import shelve
import threading

from loguru import logger

from utils import BaseWithPrettyStrMethod


class State:
    states: dict = dict()

    def __init__(
        self, default_value=None, store_to_disk=False, shelf_path="states"
    ):
        """
        Initializes the State, sets the default value, if it should be stored to
        disk and the path to the shelf.
        """
        self._value = default_value
        self._store_to_disk = store_to_disk
        self._shelf_path = shelf_path
        self._lock = threading.Lock()
        self._cached_value = None

    def __set_name__(self, owner, name):
        """
        Sets the name of the state, this is used to store the state in the states
        dict.
        """
        self.name = f"{getattr(owner, 'name', owner.__name__)}_{name}"
        self.states[self.name] = self

    def __get__(self, instance, owner):
        """
        Gets the value of the state, if it should be stored to disk it will be
        loaded from the shelf.
        """
        if instance is None:
            return self
        if self._cached_value is None:
            if self._store_to_disk:
                with shelve.open(self._shelf_path) as shelf:
                    self._cached_value = shelf.get(self.name, self._value)
            else:
                self._cached_value = self._value
        return self._cached_value

    def __set__(self, instance, value):
        """
        Sets the value of the state, if it should be stored to disk it will be
        stored in the shelf.
        """
        logger.debug(f"State {self.name} set to {value}")
        if self._store_to_disk:
            with shelve.open(self._shelf_path) as shelf:
                shelf[self.name] = value
        self._cached_value = value

    def __str__(self):
        return (
            f"{self.__class__.__name__}({self._value!r}, "
            f"{self._store_to_disk!r}, {self._shelf_path!r})"
        )


class States(BaseWithPrettyStrMethod):
    # example
    header_button_was_clicked = State(default_value=False, store_to_disk=False)
    # lockbox
    lockbox_is_locked = State(default_value=False, store_to_disk=True)
    lockbox_is_closed = State(default_value=False, store_to_disk=True)
    lockbox_curr_weight_grams = State(store_to_disk=True)
    # morning programming
    morning_programming_is_pending = State(
        default_value=False, store_to_disk=True
    )
    morning_programming_is_running = State(
        default_value=False, store_to_disk=True
    )
    morning_programming_is_finished = State(
        default_value=False, store_to_disk=True
    )
    # alarm
    alarm_is_on = State(default_value=False, store_to_disk=True)
    alarm_hour = State(default_value=0, store_to_disk=True)
    alarm_minute = State(default_value=0, store_to_disk=True)


states = States()
logger.debug(f"Created states: {states}")
