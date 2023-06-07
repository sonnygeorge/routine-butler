from nicegui import ui


def target_duration_slider(duration_minutes, duration_enabled):
    with ui.row() as root:
        root.classes("container flex items-center justify-center")

        ui.label("Target Duration:")

        target_duration_slider = ui.slider(
            min=0, max=120, value=duration_minutes
        ).classes("w-48")

        ui.label().style("width: 24px").bind_text_from(
            target_duration_slider, "value"
        )

        ui.label("minutes")

        target_duration_enabled = ui.switch(value=duration_enabled).props(
            "dense"
        )

    return target_duration_slider, target_duration_enabled
