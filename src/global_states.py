import shelve
import threading

import rich
from loguru import logger


class State:
    states = dict()

    def __init__(self, default_value=None, store_to_disk=False, shelf_path="states"):
        """Initializes the State, sets the default value, if it should be stored to disk and the path to the shelf."""
        logger.debug(
            f"Creating State: {self.__class__.__name__}({default_value!r}, {store_to_disk!r}, {shelf_path!r})"
        )
        self._value = default_value
        self._store_to_disk = store_to_disk
        self._shelf_path = shelf_path
        self._lock = threading.Lock()
        self._cached_value = None

    def __set_name__(self, owner, name):
        """Sets the name of the state, this is used to store the state in the states dict."""
        self.name = f"{getattr(owner, 'name', owner.__name__)}_{name}"
        self.states[self.name] = self

    def __get__(self, instance, owner):
        """Gets the value of the state, if it should be stored to disk it will be loaded from the shelf."""
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
        """Sets the value of the state, if it should be stored to disk it will be stored in the shelf."""
        if self._store_to_disk:
            with shelve.open(self._shelf_path) as shelf:
                shelf[self.name] = value
        self._cached_value = value

    def __str__(self):
        return f"{self.__class__.__name__}({self._value!r}, {self._store_to_disk!r}, {self._shelf_path!r})"


class States:
    # example
    header_button_was_clicked = State(default_value=False, store_to_disk=False)
    # lockbox
    lockbox_is_locked = State(default_value=False, store_to_disk=True)
    lockbox_is_closed = State(default_value=False, store_to_disk=True)
    lockbox_curr_weight_grams = State(store_to_disk=True)
    # morning programming
    morning_programming_is_pending = State(default_value=False, store_to_disk=True)
    morning_programming_is_running = State(default_value=False, store_to_disk=True)
    morning_programming_is_finished = State(default_value=False, store_to_disk=True)
    # alarm
    alarm_on = State(default_value=False, store_to_disk=True)
    alarm_time = State(default_value=False, store_to_disk=True)

    def __str__(self):
        _dict = {
            attr: getattr(self, attr)
            for attr in dir(self)
            if not callable(getattr(self, attr)) and not attr.startswith("__")
        }
        title = f"<class '{self.__class__.__module__}.{self.__class__.__name__}'> "
        return title + rich.pretty.pretty_repr(_dict)


states = States()
