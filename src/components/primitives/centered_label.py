import remi


class CenteredLabel(remi.gui.VBox):
    """Intended as an extention of remi.gui.label, but with text centered horizontally and vertically out-of-the-box."""

    def __init__(self, text: str):
        remi.gui.VBox.__init__(self)
        self.css_height = "100%"

        self.inner_label = remi.gui.Label(text)

        self.append(self.inner_label)

        self.css_border_color = "purple"
        self.css_border_width = "2px"
        self.css_border_style = "solid"

    def set_text(self, text: str):
        self.inner_label.set_text(text)
