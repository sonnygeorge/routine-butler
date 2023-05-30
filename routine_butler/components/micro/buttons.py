from typing import Tuple

from nicegui import ui

from routine_butler.components.primitives import SVG
from routine_butler.constants import ABS_REWARD_SVG_PATH, ICON_STRS


def add_button() -> ui.button:
    return ui.button().props(f"icon={ICON_STRS.add}")


def delete_button() -> ui.button:
    button = ui.button().props(f"icon={ICON_STRS.delete} color=negative")
    return button.classes("w-20")


def order_buttons(color_alias: str) -> Tuple[ui.button, ui.button]:
    frame = ui.element("div").classes("bg-gray-100 p-1 rounded")
    with frame.classes("flex flex-row items-center"):
        up_button = (
            ui.button()
            .classes(f"bg-{color_alias} w-16")
            .props(f"icon={ICON_STRS.up_arrow} dense")
        )
        ui.separator().classes("bg-gray-300 m-1.5").props("vertical")
        down_button = (
            ui.button()
            .classes(f"bg-{color_alias} w-16")
            .props(f"icon={ICON_STRS.down_arrow} dense")
        )

    return up_button, down_button


def play_button() -> ui.button:
    return ui.button().props(f"icon={ICON_STRS.play} color=positive")


def reward_button() -> ui.button:
    reward_button = ui.button().classes("bg-secondary")
    with reward_button:
        SVG(
            ABS_REWARD_SVG_PATH,
            size=17,
            color="white",
        )
    return reward_button


def save_button() -> ui.button:
    return ui.button().props(f"icon={ICON_STRS.save}")
