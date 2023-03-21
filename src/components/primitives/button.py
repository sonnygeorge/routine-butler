import remi


class Button(remi.gui.Button):
    """Extension of remi.gui.Button with default css values set for buttons across the app."""

    def __init__(self, *args, **kwargs):
        remi.gui.Button.__init__(self, *args, **kwargs)
        self.set_style({"box-shadow": "1px 1px 1px #000000"})
        self.css_height = "80%"
        self.css_width = "100%"
        self.css_margin = "1px"
