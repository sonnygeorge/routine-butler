from typing import Tuple

from nicegui import ui

from routine_butler.components.primitives import SVG
from routine_butler.constants import ABS_REWARD_SVG_PATH, ICON_STRS, SVG_SIZE


def add_button() -> ui.button:
    return ui.button().props(f"icon={ICON_STRS.add}")


def delete_button() -> ui.button:
    return ui.button().props(f"icon={ICON_STRS.delete} color=negative")


def order_buttons(color_alias: str) -> Tuple[ui.button, ui.button]:
    order_buttons_row = ui.row().classes("gap-x-1 justify-center")
    with order_buttons_row.style("width: 18%;"):
        up_button = ui.button().classes(f"bg-{color_alias}")
        up_button.props(f"icon={ICON_STRS.up_arrow} dense")
        down_button = ui.button().classes(f"bg-{color_alias}")
        down_button.props(f"icon={ICON_STRS.down_arrow} dense")
    return up_button, down_button


def play_button() -> ui.button:
    return ui.button().props(f"icon={ICON_STRS.play} color=positive")


def reward_button() -> ui.button:
    reward_button = ui.button().classes("items-center bg-secondary")
    with reward_button:
        SVG(
            ABS_REWARD_SVG_PATH,
            size=SVG_SIZE.REWARD,
            color="white",
        )
    return reward_button


def save_button() -> ui.button:
    return ui.button().props(f"icon={ICON_STRS.save}")
