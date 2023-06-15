from nicegui import ui

from routine_butler.components.header import Header
from routine_butler.constants import PagePath
from routine_butler.state import state
from routine_butler.utils import (
    apply_color_theme,
    check_for_alarm_to_ring,
    redirect_if_user_is_none,
)


@ui.page(path=PagePath.HOME)
def home():
    redirect_if_user_is_none(state.user)
    apply_color_theme()
    Header()
    ui.timer(60, lambda: check_for_alarm_to_ring(state))
