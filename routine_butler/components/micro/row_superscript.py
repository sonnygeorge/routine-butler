from nicegui import ui

# TODO color_alias type hint could be an Enum


def row_superscript(value: str, color_alias: str) -> ui.label:
    return ui.label(f"{value}.").classes(
        f"rounded bg-{color_alias} self-center	w-8 text-center text-white"
    )
