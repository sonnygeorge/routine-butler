from typing import Union

from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.plugins._check import (
    NUMERIC_VALIDATORS,
    CheckRunData,
    ConfidenceInterval,
)

GUI_COMPONENT_WIDTH_PX = 780
ROW_CLASSES = "w-11/12 my-4 items-center justify-around"

SLIDER_WIDTH_PX = int(GUI_COMPONENT_WIDTH_PX * 0.4)
INPUT_WIDTH_PX = int(GUI_COMPONENT_WIDTH_PX * 0.23)


def confidence_interval_input(
    value: Union[str, float], label: str
) -> ui.input:
    input = micro.input(
        value=value,
        label=label,
        validation=NUMERIC_VALIDATORS,
    ).props("standout dense")
    return input.style(f"width: {INPUT_WIDTH_PX}px;")


def confidence_slider_label(value: Union[str, float]) -> ui.label:
    label_txt = "Level of confidence value within interval:"
    with ui.row().classes("items-center gap-1.5"):
        ui.label(label_txt).classes("text-sm text-gray-600")
        return ui.label(value).classes("bg-gray-500 text-white rounded px-1")


def confidence_slider() -> ui.slider:
    default_value = 0.95
    with ui.row().classes(ROW_CLASSES):
        micro.vertical_separator()
        slider = ui.slider(
            min=0.5,
            max=1.0,
            step=0.01,
            value=default_value,
        ).style(f"width: {SLIDER_WIDTH_PX}px;")
        micro.vertical_separator()
        label = confidence_slider_label(default_value)
        label.bind_text_from(slider, "value")
        micro.vertical_separator()
    return slider


class NumericRangeCheckGui:
    def __init__(self, data: "NumericRangeCheck", on_complete: callable):
        self.on_complete = on_complete

        card = micro.card().classes("flex flex-col items-center")
        with card.style(f"width: {GUI_COMPONENT_WIDTH_PX}px"):
            # Display checkable prompt
            ui.markdown(f"# {data.checkable_prompt}")
            ui.separator()
            # Add interval inputs
            with ui.row().classes(ROW_CLASSES):
                micro.vertical_separator()
                self.min_estimate_input = confidence_interval_input(
                    value="",
                    label=f"min estimate ({data.units})",
                )
                micro.vertical_separator()
                self.best_estimate_input = confidence_interval_input(
                    value="",
                    label=f"best estimate ({data.units})",
                )
                micro.vertical_separator()
                self.max_estimate_input = confidence_interval_input(
                    value="",
                    label=f"max estimate ({data.units})",
                )
                micro.vertical_separator()
            ui.separator()
            # Add confidence level slider
            self.slider = confidence_slider()
            ui.separator()
            # Add enter button
            enter_button = ui.button("Enter", on_click=self.hdl_enter)
            enter_button.set_visibility(False)
            ui.timer(
                data.wait_seconds,
                lambda: enter_button.set_visibility(True),
                once=True,
            )

    def hdl_enter(self):
        min = self.min_estimate_input.value
        best = self.best_estimate_input.value
        max = self.max_estimate_input.value
        for value in [min, best, max]:
            for msg, fn in NUMERIC_VALIDATORS.items():
                if not fn(value):
                    ui.notify(msg)
                    return
        if not (min <= best <= max):
            ui.notify("Best estimate must be between min and max estimates")
            return
        ci = ConfidenceInterval(
            estimate=self.best_estimate_input.value,
            lower_bound=self.min_estimate_input.value,
            upper_bound=self.max_estimate_input.value,
            confidence=0.95,
        )
        self.on_complete(CheckRunData(reported_value=ci))


class NumericRangeCheck(BaseModel):
    checkable_prompt: str = "Do the thing!"
    units = ""
    wait_seconds: int = 0

    def administer(self, on_complete: callable):
        NumericRangeCheckGui(self, on_complete=on_complete)
