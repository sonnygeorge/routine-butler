from nicegui import ui


def card():
    card = ui.card().props("bordered")
    return card.classes("rounded-borders border-gray-200 shadow-none")
