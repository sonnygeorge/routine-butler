from nicegui import ui

from routine_butler.components.primitives.svg import SVG
from routine_butler.constants import ABS_REWARD_SVG_PATH, REWARD_SVG_SIZE


def reward_icon_placeholder() -> ui.element:
    placeholder = ui.element("q-item").props("dense").style("height: 2.5rem;")
    cls = "items-center justify-center border-secondary"
    cls += " rounded w-full border-dotted border-2"
    placeholder.classes(cls)
    with placeholder:
        SVG(
            ABS_REWARD_SVG_PATH,
            size=REWARD_SVG_SIZE,
            color="#e5e5e5",
        )
    return placeholder
