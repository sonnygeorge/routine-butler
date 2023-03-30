class icons:  # Quasar material icons
    app = "token"
    settings = "settings"
    config = "settings_input_component"
    sidebar = "menu"
    add_alarm = "alarm_add"
    gdrive = "add_to_drive"
    lock = "lock_outline"
    unlock = "lock_open"
    start = "not_started"
    person = "accessibility_new"
    panels = "dashboard"
    check = "done"


class clrs:
    black = "#0a0908"
    dark_gray = "#22333b"
    gray = "#3c4858"
    beige = "#eae0d5"
    dark_green = "#3e5641"


if __name__ in {"__main__", "__mp_main__"}:
    from nicegui import ui

    def get_values(cls):
        return [v for k, v in cls.__dict__.items() if not k.startswith("__")]

    with ui.row().classes("place-content-center"):
        for icon in get_values(icons):
            ui.icon(icon)

    with ui.row().classes("place-content-center"):
        for color in get_values(clrs):
            c = ui.card().style(f"background-color: {color};")

    ui.run()
