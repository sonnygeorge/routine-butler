from nicegui import ui

from routine_butler.constants import CLR_CODES
from routine_butler.models.user import User
from routine_butler.state import state


def apply_color_theme():
    ui.colors(
        primary=CLR_CODES.primary,
        secondary=CLR_CODES.secondary,
        accent=CLR_CODES.accent,
        positive=CLR_CODES.positive,
        negative=CLR_CODES.negative,
        info=CLR_CODES.info,
        warning=CLR_CODES.warning,
    )


def redirect_if_not_logged_in():
    def _redirect_if_not_logged_in():
        if not isinstance(state.user, User):
            ui.open("/login")

    ui.timer(0.1, _redirect_if_not_logged_in, once=True)


def move_up_in_list(list_: list, idx_to_move: int):
    list_.insert(idx_to_move - 1, list_.pop(idx_to_move))


def move_down_in_list(list_: list, idx_to_move: int):
    list_.insert(idx_to_move + 1, list_.pop(idx_to_move))
