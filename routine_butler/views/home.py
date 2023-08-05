from nicegui import ui

from routine_butler.globals import PagePath
from routine_butler.state import state
from routine_butler.utils.misc import initialize_page


@ui.page(path=PagePath.HOME)
def home():
    initialize_page(PagePath.HOME, state=state)
