from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.globals import TIME_ESTIMATION
from routine_butler.plugins._check import CheckRunData


class BinaryCheckGui:
    def __init__(self, data: "BinaryCheck", on_complete: callable):
        self.on_complete = on_complete

        with micro.card().classes("flex flex-col items-center"):
            # Display checkable prompt
            ui.markdown(f"**{data.checkable_prompt}**")
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
        self.on_complete(CheckRunData(reported_value=True))

    def hdl_failure(self):
        self.on_complete(CheckRunData(reported_value=False))


class BinaryCheck(BaseModel):
    checkable_prompt: str = "Do the thing!"
    wait_seconds: int = 0

    def administer(self, on_complete: callable):
        BinaryCheckGui(self, on_complete=on_complete)

    def estimate_duration_in_seconds(self) -> float:
        n_chars_to_read = len(self.checkable_prompt)
        read = n_chars_to_read / TIME_ESTIMATION.READING_SPEED_CHARS_PER_SECOND
        wait = self.wait_seconds * TIME_ESTIMATION.CHECK_WAIT_SECOND_MULTIPLIER
        return read + wait
