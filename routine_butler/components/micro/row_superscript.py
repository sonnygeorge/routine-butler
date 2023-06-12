from nicegui import ui

# TODO color_alias type hint could be an Enum


def row_superscript(value: str, color_alias: str) -> ui.label:
    label_frame = ui.element("div").style("width: 20px;")
    label_frame.classes("mx-0 self-start")
    label_frame.classes(f"rounded bg-{color_alias} drop-shadow")
    label_frame.classes("flex flex-col justify-center items-center")
    with label_frame:
        label = ui.label(f"{value}.")
        label.classes("text-white text-center text-s text-bold")
    return label
