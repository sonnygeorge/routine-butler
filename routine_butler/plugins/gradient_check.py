from typing import List

from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.plugins._check import CheckRunData

REFERENCES_DELINEATOR = ";"
SLIDER_WIDTH_PX: int = 540
LABEL_GAP_PX: int = 10
BRACKET_HEIGHT_MULTIPLIER = 114 / 400
MAX_LABEL_WIDTH_PX = 130
TRACK_SIZE_PX = 15
THUMB_SIZE_PX = 20


def reference_label(text: str, width_px: int) -> None:
    if width_px > MAX_LABEL_WIDTH_PX:
        width_px = MAX_LABEL_WIDTH_PX
    adjusted_width_px = width_px - LABEL_GAP_PX - 1
    with ui.column().classes("items-center justify-end gap-0 mt-2"):
        label = ui.label(text).style("font-size: 0.75rem")
        micro.curly_bracket_svg(
            width=adjusted_width_px,
            height=BRACKET_HEIGHT_MULTIPLIER * adjusted_width_px,
            color="lightgray",
        )
    label.style(f"margin: 0px {LABEL_GAP_PX / 2}px 0px {LABEL_GAP_PX / 2}px")
    label.style("padding: 6px")
    label.style(f"width: {adjusted_width_px}px")
    label.classes("bg-gray-400 rounded text-center text-white font-semibold")


def slider_with_reference_points(references: List[str]) -> ui.slider:
    frame = ui.element("div").style(f"width: {SLIDER_WIDTH_PX}px")
    with frame.classes("mx-8 my-4"):
        # reference labels
        references = references.split(REFERENCES_DELINEATOR)
        offset_increment_px = SLIDER_WIDTH_PX / (len(references))
        with ui.row().classes("justify-between items-end gap-0 w-full"):
            for reference_str in references:
                reference_label(reference_str, offset_increment_px)
        # slider
        slider = ui.slider(min=0, max=1, step=0.01, value=0.5)
        slider.classes("w-100")
        slider.props(
            f"track-size={TRACK_SIZE_PX}px thumb-size={THUMB_SIZE_PX}px"
        )
    return slider


class GradientCheckGui:
    def __init__(self, data: "GradientCheck", on_complete: callable):
        self.on_complete = on_complete

        with micro.card().classes("flex flex-col items-center"):
            # Display checkable prompt
            ui.markdown(f"# {data.checkable_prompt}")
            ui.separator()
            # Add slider
            self.slider = slider_with_reference_points(data.references)
            ui.separator()
            # Add enter buttons
            enter_button = ui.button("Enter", on_click=self.hdl_enter)
            enter_button.set_visibility(False)
            ui.timer(
                data.wait_seconds,
                lambda: enter_button.set_visibility(True),
                once=True,
            )

    def hdl_enter(self):
        self.on_complete(CheckRunData(reported_value=self.slider.value))


class GradientCheck(BaseModel):
    checkable_prompt: str = "Do the thing!"
    references: str = ""
    wait_seconds: int = 0

    def administer(self, on_complete: callable):
        GradientCheckGui(self, on_complete=on_complete)
