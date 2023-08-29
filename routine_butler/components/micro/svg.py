import os
import re
from functools import partial
from typing import Optional, Union

from nicegui import ui

from routine_butler.globals import (
    APP_LOGO_SVG_PATH,
    CURLY_BRACKET_SVG_PATH,
    PROGRAM_SVG_PATH,
    REWARD_SVG_PATH,
    ROUTINE_SVG_PATH,
)

# possible improvement: using an xml-parsing library instead of regex

HEIGHT_PATTERN = re.compile(r"height\s*=\s*[\"\'](\d+(?:\.\d*)?)(px)?[\"\']")
WIDTH_PATTERN = re.compile(r"width\s*=\s*[\"\'](\d+(?:\.\d*)?)(px)?[\"\']")
FILL_PATTERN = re.compile(r"(?<=fill:)\s*(.*?)(?=;|\")")
STROKE_PATTERN = re.compile(r"(?<=stroke:)\s*(.*?)(?=;|\")")


def update_svg_attributes(
    svg_str: str,
    size: Optional[int] = None,
    color: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
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
        if re.search(HEIGHT_PATTERN, svg_str):
            svg_str = HEIGHT_PATTERN.sub(f'height="{size}"', svg_str)
        else:
            svg_str = svg_str.replace("<svg", f'<svg height="{size}"')
        if re.search(WIDTH_PATTERN, svg_str):
            svg_str = WIDTH_PATTERN.sub(f'width="{size}"', svg_str)
        else:
            svg_str = svg_str.replace("<svg", f'<svg width="{size}"')

    if width is not None:
        if re.search(WIDTH_PATTERN, svg_str):
            svg_str = WIDTH_PATTERN.sub(f'width="{width}"', svg_str)
        else:
            svg_str = svg_str.replace("<svg", f'<svg width="{width}"')

    if height is not None:
        if re.search(HEIGHT_PATTERN, svg_str):
            svg_str = HEIGHT_PATTERN.sub(f'height="{height}"', svg_str)
        else:
            svg_str = svg_str.replace("<svg", f'<svg height="{height}"')

    if color is not None:
        if "style=" not in svg_str:
            svg_str = svg_str.replace("<path", '<path style=""')

        if re.search(FILL_PATTERN, svg_str):
            svg_str = FILL_PATTERN.sub(color, svg_str)
        else:
            svg_str = svg_str.replace('style="', f'style="fill:{color}; ')

        if re.search(STROKE_PATTERN, svg_str):
            svg_str = STROKE_PATTERN.sub(color, svg_str)
        else:
            svg_str = svg_str.replace('style="', f'style="stroke:{color}; ')

    return svg_str


def svg(
    fpath: Union[str, os.PathLike],
    size: Optional[int] = None,
    color: str = "white",
    height: Optional[int] = None,
    width: Optional[int] = None,
) -> ui.html:
    """Custom element that renders an svg file with the given size and color

    Args:
        fpath (Union[str, os.PathLike]): path to svg file
        size (int): size of svg
        color (str, optional): color of svg. Defaults to "white".
    """
    with open(fpath) as f:
        svg_str = f.read()
    svg_str = update_svg_attributes(svg_str, size, color, width, height)
    return ui.html(content=svg_str)


program_svg = partial(svg, PROGRAM_SVG_PATH)
reward_svg = partial(svg, REWARD_SVG_PATH)
routine_svg = partial(svg, ROUTINE_SVG_PATH)
app_logo_svg = partial(svg, APP_LOGO_SVG_PATH)
curly_bracket_svg = partial(svg, CURLY_BRACKET_SVG_PATH)
