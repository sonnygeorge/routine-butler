from nicegui import ui

from routine_butler.components.primitives.svg import SVG
from routine_butler.constants import ABS_REWARD_SVG_PATH, REWARD_SVG_SIZE


def reward_button() -> ui.button:
    reward_button = ui.button().classes("items-center bg-secondary")
    with reward_button:
        SVG(
            ABS_REWARD_SVG_PATH,
            size=REWARD_SVG_SIZE,
            color="white",
        )
    return reward_button
