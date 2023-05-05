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
) -> str:
    """Updates the height, width, fill, and stroke attributes of an svg string

    Args:
        svg (str): svg string
        size (Optional[int], optional): size in pixels. Defaults to None.
        color (Optional[str], optional): color in hex or rgb. Defaults to None.
    Returns:
        str: updated svg string
    """
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
    def __init__(
        self, fpath: Union[str, os.PathLike], size: int, color: str = "white"
    ):
        """Custom element that renders an svg file with the given size and color

        Args:
            fpath (Union[str, os.PathLike]): path to svg file
            size (int): size of svg
            color (str, optional): color of svg. Defaults to "white".
        """

        with open(fpath) as f:
            svg = f.read()

        svg = update_svg_attributes(svg, size, color)

        super().__init__(content=svg)
