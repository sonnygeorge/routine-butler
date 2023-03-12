from typing import Dict
import threading
import shelve

class GlobalStateManager():
    _lock = threading.Lock()

    def __init__(self):
        with self._lock:
            shelf = shelve.open("global_state_data", writeback=True)
            shelf["clicked"] = False

    
    def update(self, updates: Dict[str, any]):
        with self._lock:
            shelf = shelve.open("global_state_data", writeback=True)
            shelf.update(updates)


    def read(self):
        with self._lock:
            return(shelve.open("global_state_data"))


global_state = GlobalStateManager()
