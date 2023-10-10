from nicegui import ui

from routine_butler.utils.misc import close_keyboard, open_keyboard


def text_area(*args, **kwargs) -> ui.textarea:
    input = ui.textarea(*args, **kwargs)
    input.on("focus", open_keyboard)
    input.on("blur", close_keyboard)
    return input
