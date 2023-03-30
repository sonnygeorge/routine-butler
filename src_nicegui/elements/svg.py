import os
import re
from typing import Union

from nicegui import ui

HEIGHT_PATTERN = r'height\s*=\s*["\'](\d+(?:\.\d*)?)(px)?["\']'
WIDTH_PATTERN = r'width\s*=\s*["\'](\d+(?:\.\d*)?)(px)?["\']'


class SVG(ui.html):
    """Wraps nicegui.ui.html for reading an svg from a file and setting its
    height and width to the size parameter"""

    def __init__(self, fpath: Union[str, os.PathLike], size: int):
        with open(fpath) as f:
            svg = f.read()
        if "height=" in svg:
            svg = re.compile(HEIGHT_PATTERN).sub(f'height="{size}"', svg)
        else:
            svg = svg.replace("<svg", f'<svg height="{size}"')
        if "width=" in svg:
            svg = re.compile(WIDTH_PATTERN).sub(f'width="{size}"', svg)
        else:
            svg = svg.replace("<svg", f'<svg width="{size}"')
        super().__init__(content=svg)
