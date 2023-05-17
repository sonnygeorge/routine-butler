from nicegui import ui

from routine_butler.components.header import Header
from routine_butler.constants import PagePath
from routine_butler.state import state
from routine_butler.utils import apply_color_theme, redirect_if_user_is_none


@ui.page(path=PagePath.HOME)
def home():
    redirect_if_user_is_none(state.user)
    apply_color_theme()
    Header()
