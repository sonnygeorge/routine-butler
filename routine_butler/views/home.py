from nicegui import ui

from routine_butler.configs import PagePath
from routine_butler.state import state
from routine_butler.utils import initialize_page


@ui.page(path=PagePath.HOME)
def home():
    initialize_page(PagePath.HOME, state=state)
