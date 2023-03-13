from typing import Protocol


class Performer(Protocol):
    name: str

    def should_be_on_stage(self) -> bool:
        """returns True if the performer should be on the stage, False otherwise"""
        ...

    def do_stuff(self):
        """gets called by the app's idle loop"""
        ...
