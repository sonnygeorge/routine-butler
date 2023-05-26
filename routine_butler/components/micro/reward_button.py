from nicegui import ui

from routine_butler.components.primitives import SVG
from routine_butler.constants import ABS_REWARD_SVG_PATH, SVG_SIZE


def reward_button() -> ui.button:
    reward_button = ui.button().classes("items-center bg-secondary")
    with reward_button:
        SVG(
            ABS_REWARD_SVG_PATH,
            size=SVG_SIZE.REWARD,
            color="white",
        )
    return reward_button
