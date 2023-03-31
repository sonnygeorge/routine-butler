from nicegui import ui

from elements.header import Header


class Time:
    time = "03:10"


def build_ui():
    Header()

    with ui.input("hours").props("filled").bind_value(Time, "time") as hours:
        with hours.add_slot("append"):
            with ui.icon("access_time").classes("cursor-pointer"):
                with ui.element("q-popup-proxy").props(
                    'cover transition-show="scale" transition-hide="scale"'
                ):
                    ui.time().bind_value(Time, "time")


def main():
    build_ui()
    ui.run()


if __name__ == "__main__":
    main()
