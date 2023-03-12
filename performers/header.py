import time
from threading import Timer

import remi

from performers.performer import Performer, PerformerContainer
from global_state import global_state


class HeaderContainer(PerformerContainer, remi.gui.HBox):
    def __init__(self, name, app_instance):
        remi.gui.HBox.__init__(self)
        self.name = name
        self.app_instance = app_instance

        self.css_height = "60.0px"
        self.css_width = "795.0px"
        self.css_border_width = "2px"
        self.css_border_color = "gray"
        self.css_border_style = "dashed"

        header_text = remi.gui.TextInput()
        header_text.css_height = "30px"
        header_text.css_width = "30%"
        header_text.text = "This is the header for the app."
        self.append(header_text, "header_text")

        self.button = remi.gui.Button()
        self.button.text = "not clicked"
        self.button.onclick.do(self.on_button_clicked)
        self.append(self.button, 'button')

        self.clock = remi.gui.TextInput()
        self.clock.css_height = "30px"
        self.clock.css_width = "12%"
        self.clock.text = "00:00:00"
        self.append(self.clock, "clock")

        self.update_time()

    def on_button_clicked(self, _):
        button_was_already_clicked = global_state.read()["clicked"]
        if button_was_already_clicked:
            # We "unclick" the button
            global_state.update({"clicked": False})
            self.button.text = "not clicked"
        else:
            # We "click" the button
            global_state.update({"clicked": True})
            self.button.text = "clicked"
        
    def update_time(self):
        t = time.localtime()
        t_str = f"{t.tm_hour}:{t.tm_min}:{t.tm_sec}"
        with self.app_instance.update_lock:
            self.clock.set_text(t_str)

        Timer(1, self.update_time).start()


class Header(Performer):
    def __init__(self, name: str, app_instance: remi.server.App):
        self.container = HeaderContainer(name, app_instance)

    def should_be_on_stage(self):
        # We want the header to always be "on stage"
        return True
