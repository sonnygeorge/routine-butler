from nicegui import ui


def target_duration_slider(duration_minutes, duration_enabled):
    with ui.row().classes("items-center justify-center"):

        ui.label("Target Duration:")

        target_duration_slider = ui.slider(
            min=0, max=120, value=duration_minutes
        ).classes("w-48")

        label_classes = "text-white text-center text-s"

        minutes_display = ui.element("div").classes("flex items-center")
        with minutes_display.classes("flex-row gap-x-0 rounded bg-gray-400"):
            dark_frame = ui.element("div").classes("flex bg-primary rounded")
            with dark_frame.classes("flex-row items-center justify-center"):
                label = ui.label()
                label.bind_text_from(target_duration_slider, "value")
                label.classes(label_classes + " text-bold mx-2")

            ui.label("minutes").classes(label_classes + " ml-1 mr-2")

        target_duration_enabled = ui.switch(value=duration_enabled)
        target_duration_enabled.props("dense")

    return target_duration_slider, target_duration_enabled
