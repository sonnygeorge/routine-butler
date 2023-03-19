import remi


class BodyContainer(remi.gui.VBox):
    """VBox-style container for the body of the app."""

    def __init__(self):
        remi.gui.VBox.__init__(
            self, width="100%", style={"margin": "23px 0px", "background": "none"}
        )
