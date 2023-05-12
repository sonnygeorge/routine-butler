from typing import Tuple

from nicegui import ui

from routine_butler.constants import ICON_STRS

# TODO: color_alias type hint could be Enum


def order_buttons(color_alias: str) -> Tuple[ui.button, ui.button]:
    order_buttons_row = ui.row().classes("gap-x-1 justify-center")
    with order_buttons_row.style("width: 18%;"):
        up_button = ui.button().classes(f"bg-{color_alias}")
        up_button.props(f"icon={ICON_STRS.up_arrow} dense")
        down_button = ui.button().classes(f"bg-{color_alias}")
        down_button.props(f"icon={ICON_STRS.down_arrow} dense")
    return up_button, down_button
