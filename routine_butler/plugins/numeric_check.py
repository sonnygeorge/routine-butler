from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.globals import TIME_ESTIMATION
from routine_butler.plugins._check import NUMERIC_VALIDATORS, CheckRunData


class NumericCheckGui:
    def __init__(self, data: "NumericCheck", on_complete: callable):
        self.on_complete = on_complete

        with micro.card().classes("flex flex-col items-center"):
            # Display checkable prompt
            ui.markdown(f"**{data.checkable_prompt}**")
            # Add input
            self.input = micro.input(
                value="",
                label=f"({data.units})",
                validation=NUMERIC_VALIDATORS,
            )
            # Add enter button
            enter_button = ui.button("Enter", on_click=self.hdl_enter)
            enter_button.set_visibility(False)
            ui.timer(
                data.wait_seconds,
                lambda: enter_button.set_visibility(True),
                once=True,
            )

    def hdl_enter(self):
        for msg, fn in NUMERIC_VALIDATORS.items():
            if not fn(self.input.value):
                ui.notify(msg)
                return
        self.on_complete(CheckRunData(reported_value=self.input.value))


class NumericCheck(BaseModel):
    checkable_prompt: str = "Do the thing!"
    units: str = ""
    wait_seconds: int = 0

    def administer(self, on_complete: callable):
        NumericCheckGui(self, on_complete=on_complete)

    def estimate_duration_in_seconds(self) -> float:
        n_chars_to_read = len(self.checkable_prompt)
        read = n_chars_to_read / TIME_ESTIMATION.READING_SPEED_CHARS_PER_SECOND
        wait = self.wait_seconds * TIME_ESTIMATION.CHECK_WAIT_SECOND_MULTIPLIER
        return read + wait + 3.5  # 3.5 seconds for numeric entry
