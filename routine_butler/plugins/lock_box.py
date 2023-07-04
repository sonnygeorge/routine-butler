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

        box.target_grams = target_grams
        box.allowed_grams_upper_bound = tolerance_grams

        with micro.card():
            # FIXME: make this look better & show current grams on scale
            with ui.row():
                with ui.column():
                    self.scale_zeroed_indicator = status_indicator(
                        self.scale_is_zeroed
                    )
                with ui.column():
                    self.scale_indicator = status_indicator(False)
                    self.weight_label = ui.label("")
                with ui.column():
                    self.closed_indicator = status_indicator(box.is_closed())
                ui.timer(0.8, self.update_status_indicators)

            with ui.row():
                zero_scale_button = ui.button("Zero Scale")
                lock_box_button = ui.button("Lock Box")

            zero_scale_button.on("click", self.hdl_zero_scale)
            lock_box_button.on("click", self.hdl_lock_box)

    def update_status_indicators(self):
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

    def hdl_zero_scale(self):
        box.zero_scale()
        self.scale_is_zeroed = True
        self.scale_zeroed_indicator.props("color=positive")

    def hdl_lock_box(self):
        unable_message = ""
        if not self.scale_is_zeroed:
            unable_message += " --must zero the scale"
        if not box.passes_weight_check():
            unable_message += " --must place object (weight criteria not met)"
        if not box.is_closed():
            unable_message += " --must close the box all the way"

        if unable_message != "":
            ui.notify("Unable to close:" + unable_message)
        else:
            box.lock()
            ui.notify("Box locked!")
            ui.timer(1, self.on_complete, once=True)


class LockBox(BaseModel):
    target_grams: int = 200
    tolerance_grams: int = 200

    def administer(self, on_complete: callable):
        LockBoxGui(self.target_grams, self.tolerance_grams, on_complete)
