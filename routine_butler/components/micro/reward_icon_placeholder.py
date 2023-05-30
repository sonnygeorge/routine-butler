from nicegui import ui

from routine_butler.components.primitives import SVG
from routine_butler.constants import ABS_REWARD_SVG_PATH, SVG_SIZE


def reward_icon_placeholder() -> ui.element:
    placeholder = ui.element("q-item").props("dense")
    with placeholder:
        SVG(
            ABS_REWARD_SVG_PATH,
            size=SVG_SIZE.REWARD,
            color="#e5e5e5",
        )
    return placeholder
