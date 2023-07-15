import asyncio

from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.hardware import box


def status_indicator(is_positive=False) -> ui.button:
    color = "positive" if is_positive else "negative"
    return ui.button("").props(f"color={color}").classes("mx-3")


class LockBoxGui:
    def __init__(
        self, target_grams: int, tolerance_grams: int, on_complete: callable
    ):
        self.scale_is_zeroed: bool = False
        self.on_complete = on_complete

        box.set_target_grams(target_grams)
        box.set_tolerance_grams(tolerance_grams)

        with micro.card().classes("flex flex-col items-center"):
            with ui.row():
                with ui.column():
                    self.scale_zeroed_indicator = status_indicator(
                        self.scale_is_zeroed
                    )
                with ui.column().classes("items-center"):
                    self.scale_indicator = status_indicator(False)
                    self.weight_label = ui.label("Pending...")
                with ui.column():
                    self.closed_indicator = status_indicator(box.is_closed())

            with ui.row():
                self.zero_scale_button = ui.button("Zero Scale")
                self.lock_box_button = ui.button("Lock Box")

            self.zero_scale_button.on("click", self.hdl_zero_scale)
            self.lock_box_button.on("click", self.hdl_lock_box)

        self.status_check_timer = ui.timer(0.8, self._update_status_indicators)

    def _disable_buttons(self):
        self.zero_scale_button.set_visibility(False)
        self.lock_box_button.set_visibility(False)

    def _enable_buttons(self):
        self.zero_scale_button.set_visibility(True)
        self.lock_box_button.set_visibility(True)

    def _update_status_indicators(self):
        if self.scale_is_zeroed:
            scale_color = (
                "positive" if box.passes_weight_check() else "negative"
            )
            self.scale_indicator.props(f"color={scale_color}")
            if box.last_weight_measurement is not None:
                label_text = f"{round(box.last_weight_measurement)}g"
                self.weight_label.set_text(label_text)
        closed_color = "positive" if box.is_closed() else "negative"
        self.closed_indicator.props(f"color={closed_color}")

    async def hdl_zero_scale(self):
        self._disable_buttons()
        await asyncio.sleep(0.2)
        box.zero_scale()
        self.scale_is_zeroed = True
        self.scale_zeroed_indicator.props("color=positive")
        self.weight_label.set_text("0g")
        self._enable_buttons()

    async def hdl_lock_box(self):
        self._disable_buttons()
        await asyncio.sleep(0.2)

        unable_message = ""
        if not self.scale_is_zeroed:
            unable_message += " --must zero the scale"
        if not box.passes_weight_check():
            unable_message += " --must place object (weight criteria not met)"
        if not box.is_closed():
            unable_message += " --must close the box all the way"

        if unable_message != "":
            ui.notify("Unable to close:" + unable_message)
            self._enable_buttons()
        else:
            self.status_check_timer.deactivate()
            box.lock()
            ui.notify("Box locked!")
            ui.timer(1, self.on_complete, once=True)


class LockBox(BaseModel):
    target_grams: int = 2200
    tolerance_grams: int = 200

    def administer(self, on_complete: callable):
        LockBoxGui(self.target_grams, self.tolerance_grams, on_complete)
