import datetime

import remi

from performers.performer import Performer, PerformerContainer
from global_state import global_state


class ConditionalPerformerContainer(PerformerContainer, remi.gui.VBox):
    def __init__(self, name, app_instance):
        remi.gui.VBox.__init__(self)
        self.name = name
        self.app_instance = app_instance

        self.css_height = "400.0px"
        self.css_width = "795.0px"
        self.css_border_width = "2px"
        self.css_border_color = "gray"
        self.css_border_style = "dashed"

        title_box = remi.gui.HBox()
        title_box.css_height = "80px"
        title_box.css_width = "80%"
        title = remi.gui.TextInput()
        title.css_height = "80px"
        title.css_width = "100%"
        title.text = (
            'Example of a performer who knows to go onto or leave the "stage"'
            " based on its understanding of global conditions"
        )
        title_box.append(title, "title")

        content_box = remi.gui.HBox()
        content_box.css_height = "300px"
        content_box.css_width = "90%"

        header_text = remi.gui.TextInput()
        header_text.css_height = "100px"
        header_text.css_width = "50%"
        header_text.text = (
            "I am only on stage when the current second's final"
            ' digit is 0-5 and the header button is "not clicked".'
        )
        content_box.append(header_text, "header_text")

        video = remi.gui.VideoPlayer(
            "http://www.w3schools.com/tags/movie.mp4",
            "http://www.oneparallel.com/wp-content/uploads/2011/01/placeholder.jpg",
            width=300,
            height=270,
        )
        content_box.append(video, "video")

        self.append(title_box, "title_box")
        self.append(content_box, "content_box")


class ConditionalPerformer(Performer):
    def __init__(self, name: str, app_instance: remi.server.App):
        self.container = ConditionalPerformerContainer(name, app_instance)

    def should_be_on_stage(self):
        # We only want this performer "on stage" when:
        # 1. The current second's final digit is 0-5
        # 2. The header button is not "clicked"
        condition_one = 0 <= int(datetime.datetime.now().strftime("%S")) % 10 <= 5
        condition_two = not global_state.read()["clicked"]
        if condition_one and condition_two:
            return True
        else:
            return False
