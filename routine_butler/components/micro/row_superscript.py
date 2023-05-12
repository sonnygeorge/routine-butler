from nicegui import ui

# TODO color_alias type hint could be an Enum


def row_superscript(value: str, color_alias: str) -> ui.label:
    label_frame = ui.element("div").style("width: 5%;")
    label_frame.classes("mx-0 self-start w-full")
    label_frame.classes(f"rounded bg-{color_alias} w-full drop-shadow")
    with label_frame:
        label = ui.label(f"{value}.")
        label.style("height: 1.125rem;")
        label.classes("text-white text-center text-xs text-bold")
        label.classes("flex items-center justify-center")
    return label
