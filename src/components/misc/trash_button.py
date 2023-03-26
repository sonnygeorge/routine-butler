from components.primitives.button import Button


class TrashButton(Button):
    def __init__(self):
        Button.__init__(self, "🗑️")
        self.set_style({"text-shadow": "0px 0px 3px #FFFFFF"})
        self.css_background_color = "red"
        self.css_height = "23px"
        self.css_width = "23px"
