import remi

from loguru import logger

from subapps.subapp import SubApp, SubAppContainer
from states import states


def apply_button_css(button: remi.gui.Button):
    button.css_height = "35px"
    button.css_width = "35px"
    button.css_font_size = "20px"


class AlarmContainer(SubAppContainer):
    def __init__(self):
        SubAppContainer.__init__(self)

        # title
        title_box = remi.gui.HBox()
        title_box.css_height = "15%"
        title_box.css_width = "100%"
        title = remi.gui.Label("alarm")
        title.css_height = "100%"
        title.css_width = "100%"
        title_box.append(title, "title")
        self.append(title_box, "title_box")

        # alarm components
        self.alarm_box = remi.gui.HBox(margin="5px 5px")
        self.alarm_box.css_height = "85%"

        # hour plus button
        self.hour_plus_button = remi.gui.Button("+")
        apply_button_css(self.hour_plus_button)
        self.hour_plus_button.onclick.connect(self.on_hour_plus)
        self.alarm_box.append(self.hour_plus_button, "hour_plus_button")

        # hour minus button
        self.hour_minus_button = remi.gui.Button("-")
        apply_button_css(self.hour_minus_button)
        self.hour_minus_button.onclick.connect(self.on_hour_minus)
        self.alarm_box.append(self.hour_minus_button, "hour_minus_button")

        # time label
        self.time_label = remi.gui.Label("00:00")
        self.time_label.css_height = "35px"
        self.update_alarm_time_label()
        self.alarm_box.append(self.time_label, "time_label")

        # minute plus button
        self.minute_plus_button = remi.gui.Button("+")
        apply_button_css(self.minute_plus_button)
        self.minute_plus_button.onclick.connect(self.on_minute_plus)
        self.alarm_box.append(self.minute_plus_button, "minute_plus_button")

        # minute minus button
        self.minute_minus_button = remi.gui.Button("-")
        apply_button_css(self.minute_minus_button)
        self.minute_minus_button.onclick.connect(self.on_minute_minus)
        self.alarm_box.append(self.minute_minus_button, "minute_minus_button")

        # is on checkbox
        self.is_on_checkbox = remi.gui.CheckBox(checked=states.alarm_is_on)
        self.is_on_checkbox.onchange.connect(self.on_is_on_checkbox)
        self.alarm_box.append(self.is_on_checkbox, "is_on_checkbox")

        self.append(self.alarm_box, "content_box")

    def update_alarm_time_label(self):
        self.time_label.set_text(f"{states.alarm_hour:02d}:{states.alarm_minute:02d}")

    def increment_hour(self):
        if states.alarm_hour == 23:
            states.alarm_hour = 0
        else:
            states.alarm_hour += 1

    def decrement_hour(self):
        if states.alarm_hour == 0:
            states.alarm_hour = 23
        else:
            states.alarm_hour -= 1

    def increment_minute(self):
        if states.alarm_minute == 59:
            states.alarm_minute = 0
            self.increment_hour()
        else:
            states.alarm_minute += 1

    def decrement_minute(self):
        if states.alarm_minute == 0:
            states.alarm_minute = 59
            self.decrement_hour()
        else:
            states.alarm_minute -= 1

    def on_hour_plus(self, _):
        logger.debug("Alarm hour incremented by user")
        self.increment_hour()
        self.update_alarm_time_label()

    def on_hour_minus(self, _):
        logger.debug("Alarm hour decremented by user")
        self.decrement_hour()
        self.update_alarm_time_label()

    def on_minute_plus(self, _):
        logger.debug("Alarm minute incremented by user")
        self.increment_minute()
        self.update_alarm_time_label()

    def on_minute_minus(self, _):
        logger.debug("Alarm minute decremented by user")
        self.decrement_minute()
        self.update_alarm_time_label()

    def on_is_on_checkbox(self, _, is_checked):
        logger.debug(f"Alarm is_on checkbox changed to {is_checked}")
        states.alarm_is_on = is_checked


# TODO write what to do when alarm time is reach (it should go off)


class Alarm(SubApp):
    def __init__(self, name: str):
        SubApp.__init__(self, name=name, container=AlarmContainer())

    def should_be_on_stage(self):
        return True

    def do_stuff(self):
        pass
