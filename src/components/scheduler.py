import remi

from components.primitives.button import Button
from components.primitives.centered_label import CenteredLabel
from components.primitives.configurer import Configurer
from schema.schedule import Schedule

BUTTON_BOX_WIDTH = "15%"


class Scheduler(Configurer):
    """A component that offers controls to configure a Schedule object."""

    def __init__(self, schedule: Schedule):
        Configurer.__init__(self)

        self.schedule = schedule

        # hour buttons
        self.hour_buttons = remi.gui.HBox(height="100%", width=BUTTON_BOX_WIDTH)
        self.append(self.hour_buttons, "hour_buttons")

        # hour plus button
        self.hour_plus_button = Button("+")
        self.hour_plus_button.onclick.connect(self.on_hour_plus)
        self.hour_buttons.append(self.hour_plus_button, "hour_plus_button")

        # hour minus button
        self.hour_minus_button = Button("-")
        self.hour_minus_button.onclick.connect(self.on_hour_minus)
        self.hour_buttons.append(self.hour_minus_button, "hour_minus_button")

        # time label
        self.time_label = CenteredLabel("00:00")
        self.update_alarm_time_label()
        self.append(self.time_label, "time_label")

        # minute buttons
        self.minute_buttons = remi.gui.HBox(height="100%", width=BUTTON_BOX_WIDTH)
        self.append(self.minute_buttons, "minute_buttons")

        # minute plus button
        self.minute_plus_button = Button("+")
        self.minute_plus_button.onclick.connect(self.on_minute_plus)
        self.minute_buttons.append(self.minute_plus_button, "minute_plus_button")

        # minute minus button
        self.minute_minus_button = Button("-")
        self.minute_minus_button.onclick.connect(self.on_minute_minus)
        self.minute_buttons.append(self.minute_minus_button, "minute_minus_button")

        # is active label
        self.is_active_label = CenteredLabel("Is Active:")
        self.append(self.is_active_label, "is_active_label")

        # is active checkbox
        self.is_active_checkbox = remi.gui.CheckBox(checked=self.schedule.is_active)
        self.is_active_checkbox.onchange.connect(self.on_is_on_checkbox)
        self.append(self.is_active_checkbox, "is_on_checkbox")

    def update_alarm_time_label(self):
        self.time_label.set_text(f"{self.schedule.hour:02d}:{self.schedule.minute:02d}")

    def increment_hour(self):
        if self.schedule.hour == 23:
            self.schedule.hour = 0
        else:
            self.schedule.hour += 1

    def decrement_hour(self):
        if self.schedule.hour == 0:
            self.schedule.hour = 23
        else:
            self.schedule.hour -= 1

    def increment_minute(self):
        if self.schedule.minute == 59:
            self.schedule.minute = 0
            self.increment_hour()
        else:
            self.schedule.minute += 1

    def decrement_minute(self):
        if self.schedule.minute == 0:
            self.schedule.minute = 59
            self.decrement_hour()
        else:
            self.schedule.minute -= 1

    def on_hour_plus(self, _):
        self.increment_hour()
        self.update_alarm_time_label()

    def on_hour_minus(self, _):
        self.decrement_hour()
        self.update_alarm_time_label()

    def on_minute_plus(self, _):
        self.increment_minute()
        self.update_alarm_time_label()

    def on_minute_minus(self, _):
        self.decrement_minute()
        self.update_alarm_time_label()

    def on_is_on_checkbox(self, _, is_checked):
        self.schedule.is_active = is_checked
