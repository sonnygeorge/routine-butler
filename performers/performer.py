from typing import Protocol

import remi


class PerformerContainer(Protocol):
    name: str
    app_instance: remi.server.App


class Performer(Protocol):
    container: PerformerContainer

    def should_be_on_stage(self):
        ...
