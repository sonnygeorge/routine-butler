import remi


class Configurer(remi.gui.HBox):
    """
    Extension of remi.gui.HBox with default css values set for configurers across the app.

    A configurer is a component that allows the user to configure a setting.

    Within a Configurations, component, we expect to have a two-column grid of:
        column 1: the name of the thing being configured
        column 2: the Configurer component for configuring it
    """

    def __init__(self):
        remi.gui.HBox.__init__(self)
        self.css_align_self = "center"
        self.css_height = "100%"
        self.css_width = "100%"

        self.css_border_color = "cyan"
        self.css_border_width = "2px"
        self.css_border_style = "solid"
