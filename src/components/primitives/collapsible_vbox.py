from typing import List

import remi
from loguru import logger

from components.primitives.button import Button


class CollapsibleVBox(remi.gui.VBox):
    """
    An extension of Remi's VBox that is collapsable/expandable.

    Is initialized with a title, which is always displayed at the top of the box alongside the button to collapse/expand the box.
    """

    collapsed: bool = False
    collapsed_content: List[remi.gui.Container] = []

    def __init__(self, title: str = "Untitled"):
        """Adds a header container with the title and the collapse/expand button inside of it."""

        remi.gui.VBox.__init__(self)
        self.title = title

        # header
        self.header = remi.gui.HBox()
        self.header.css_width = "100%"
        self.header.css_height = "30px"
        self.header.css_align_items = "center"
        self.header.css_float = "top"
        self.append(self.header, "header")

        # title
        self.title_label_box = remi.gui.VBox(style={"padding-left": "5px"})
        self.title_label_box.css_width = "92%"
        self.title_label_box.css_font_size = "20px"
        self.title_label_box.css_align_self = "flex-start"
        self.title_label_box.css_float = "left"
        self.title_label = remi.gui.Label(self.title)
        self.title_label.css_font_size = "20px"
        self.title_label.css_font_weight = "bold"
        self.title_label.css_align_self = "flex-start"
        self.title_label_box.append(self.title_label, "title_label")
        self.header.append(self.title_label_box, "title_label_box")

        # collapse button
        self.collapse_button_text = "▼" if self.collapsed else "▲"
        self.collapse_button = Button(self.collapse_button_text)
        self.title_label_box.css_float = "right"
        self.collapse_button.css_width = "8%"
        self.collapse_button.onclick.do(self.toggle_collapse)
        self.header.append(self.collapse_button, "collapse_button")

    def toggle_collapse(self, widget: remi.gui.Widget):
        """Toggles the collapsed state of the CollapsibleVBox"""
        if self.collapsed:
            self.expand()
        else:
            self.collapse()
        self.collapsed = not self.collapsed

    def collapse(self):
        """Collapses by removing all children (except header) and storing them for later expansion"""
        # temp list to avoid RuntimeError: dictionary changed size during iteration
        children = list(self.children.values())
        # remove all children except header
        for child in children:
            if child != self.header:
                self.remove_child(child)
                self.collapsed_content.append(child)
        # change direction of button triangle to down
        self.collapse_button.set_text("▼")
        logger.debug(f"Collapsed CollapsibleVBox {self.title}...")

    def expand(self):
        """Expands by adding all children stored in collapsed_content"""
        # reintroduced previously collapsed content
        for child in self.collapsed_content:
            self.append(child)
        # set collapsed_content back to empty (since no longer collapsed)
        self.collapsed_content = []
        # change direction of button triangle to up
        self.collapse_button.set_text("▲")
        logger.debug(f"Expanded CollapsibleVBox {self.title}...")
