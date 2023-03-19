from typing import List

import remi
from loguru import logger

from components.primitive.button import Button


class CollapsibleVBox(remi.gui.VBox):
    collapsed: bool = False
    collapsed_content: List[remi.gui.Container] = []

    def __init__(self, title: str):
        remi.gui.VBox.__init__(self)
        self.title = title

        # header
        self.header = remi.gui.HBox()
        self.header.css_width = "100%"
        self.header.css_height = "30px"
        self.header.css_align_items = "center"
        self.header.css_float = "top"

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

        self.append(self.header, "header")

    def toggle_collapse(self, widget: remi.gui.Widget):
        if self.collapsed:
            self.expand()
        else:
            self.collapse()
        self.collapsed = not self.collapsed

    def collapse(self):
        children = list(self.children.values())
        for child in children:
            if child != self.header:
                self.remove_child(child)
                self.collapsed_content.append(child)
        self.collapse_button.set_text("▼")
        logger.debug(f"Collapsed CollapsibleVBox {self.title}...")

    def expand(self):
        for child in self.collapsed_content:
            self.append(child)
        self.collapsed_content = []
        self.collapse_button.set_text("▲")
        logger.debug(f"Expanded CollapsibleVBox {self.title}...")
