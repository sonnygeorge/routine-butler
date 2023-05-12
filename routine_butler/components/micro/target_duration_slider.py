from nicegui import ui


def target_duration_slider(value) -> ui.slider:
    ui.label("Target Duration:").style("width: 120px;")
    target_duration_slider = ui.slider(min=0, max=120, value=value).classes(
        "w-1/3"
    )
    target_duration_label = ui.label().style("width: 35px;")
    target_duration_label.bind_text_from(target_duration_slider, "value")
    target_duration_label.set_text(str(value))
    ui.label("minutes").style("width: 52px;").classes("text-left")
    return target_duration_slider
