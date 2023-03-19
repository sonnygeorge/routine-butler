import remi


class TopmostContainer(remi.gui.Container):
    """Container for the entire app (header, content, etc.)"""

    def __init__(self):
        remi.gui.Container.__init__(self, width="100%", height="100%")
        self.css_background_color = "lightgray"
        self.css_font_family = "Courier"
