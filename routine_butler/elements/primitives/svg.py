import os
import re
from typing import Union, Optional

from nicegui import ui

HEIGHT_PATTERN = re.compile(r"height\s*=\s*[\"\'](\d+(?:\.\d*)?)(px)?[\"\']")
WIDTH_PATTERN = re.compile(r"width\s*=\s*[\"\'](\d+(?:\.\d*)?)(px)?[\"\']")
FILL_PATTERN = re.compile(r"(?<=fill:)\s*(.*?)(?=;|\")")
STROKE_PATTERN = re.compile(r"(?<=stroke:)\s*(.*?)(?=;|\")")


def update_svg_attributes(
    svg: str, size: Optional[int] = None, color: Optional[str] = None
):
    """Updates the height, width, fill, and stroke attributes of an svg string"""
    if size is not None:
        if re.search(HEIGHT_PATTERN, svg):
            svg = HEIGHT_PATTERN.sub(f'height="{size}"', svg)
        else:
            svg = svg.replace("<svg", f'<svg height="{size}"')
        if re.search(WIDTH_PATTERN, svg):
            svg = WIDTH_PATTERN.sub(f'width="{size}"', svg)
        else:
            svg = svg.replace("<svg", f'<svg width="{size}"')

    if color is not None:
        if "style=" not in svg:
            svg = svg.replace("<path", f'<path style=""')

        if re.search(FILL_PATTERN, svg):
            svg = FILL_PATTERN.sub(color, svg)
        else:
            svg = svg.replace('style="', f'style="fill:{color}; ')

        if re.search(STROKE_PATTERN, svg):
            svg = STROKE_PATTERN.sub(color, svg)
        else:
            svg = svg.replace('style="', f'style="stroke:{color}; ')

    return svg


class SVG(ui.html):
    """Wraps nicegui.ui.html for reading an svg from a file and setting its
    height and width to the size parameter"""

    def __init__(
        self, fpath: Union[str, os.PathLike], size: int, color: str = "white"
    ):
        with open(fpath) as f:
            svg = f.read()

        svg = update_svg_attributes(svg, size, color)

        super().__init__(content=svg)
