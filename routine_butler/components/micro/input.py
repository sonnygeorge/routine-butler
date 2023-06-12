from nicegui import ui

from routine_butler.utils import close_keyboard, open_keyboard


def input(*args, **kwargs):
    input = micro.input(*args, **kwargs)
    input.on("focus", open_keyboard)
    input.on("blur", close_keyboard)
    return input
