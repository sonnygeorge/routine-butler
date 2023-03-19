import remi


class Button(remi.gui.Button):
    """Extension of remi.gui.Button with default css values set for buttons across the app."""

    def __init__(self, text: str):
        remi.gui.Button.__init__(self, text)
        self.css_height = "80%"
        self.css_width = "100%"
        self.css_margin = "1px"
