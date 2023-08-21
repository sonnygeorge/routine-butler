from typing import TypedDict

from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro


class TimedBinaryCheckRunData(TypedDict):
    reported_success: bool


class TimedBinaryCheckGui:
    def __init__(self, data: "TimedBinaryCheck", on_complete: callable):
        self.on_complete = on_complete

        with micro.card().classes("flex flex-col items-center"):
            # Display checkable prompt
            ui.markdown(f"# {data.checkable_prompt}")
            # Add buttons
            buttons_row = ui.row()
            with buttons_row:
                ui.button("Success", on_click=self.hdl_success)
                ui.button("Failure", on_click=self.hdl_failure)
            # Make buttons visible after timer
            buttons_row.set_visibility(False)
            ui.timer(
                data.wait_seconds,
                lambda: buttons_row.set_visibility(True),
                once=True,
            )

    def hdl_success(self):
        self.on_complete(TimedBinaryCheckRunData(reported_success=True))

    def hdl_failure(self):
        self.on_complete(TimedBinaryCheckRunData(reported_success=False))


class TimedBinaryCheck(BaseModel):
    checkable_prompt: str = "Do the thing!"
    wait_seconds: int = 5

    def administer(self, on_complete: callable):
        TimedBinaryCheckGui(self, on_complete=on_complete)
