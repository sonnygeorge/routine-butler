from typing import Protocol


class Performer(Protocol):
    name : str

    def __init__(self, name: str):
        self.name = name

    def should_be_on_stage(self):
        ...

    def do_stuff(self):
        #this is a function that gets called by the main application during idle loop
        # Performes will not implmenent their own threads or timers. 
        # They will perform their activities in this function.
        # This function is already a safe context, so Performes don't need to lock App.update_lock,
        #   this way there is a better separation between GUI and app specific business
        ...
