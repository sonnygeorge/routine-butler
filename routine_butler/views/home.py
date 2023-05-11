from nicegui import ui

from routine_butler.ui.header import Header
from routine_butler.utils import apply_color_theme, redirect_if_not_logged_in


@ui.page("/")
def main_gui():
    redirect_if_not_logged_in()
    apply_color_theme()
    Header()
