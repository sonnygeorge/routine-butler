from nicegui import ui


def volume_knob(value: float) -> ui.knob:
    vol_knob = ui.knob(value=value, track_color="grey-2")
    vol_knob.props("size=lg thickness=0.3")
    with vol_knob:
        ui.icon("volume_up").props("size=xs")
    return vol_knob
