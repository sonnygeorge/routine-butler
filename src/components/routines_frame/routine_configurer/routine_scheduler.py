import remi

from components.misc.trash_button import TrashButton
from components.primitives.button import Button
from components.primitives.centered_label import CenteredLabel
from database import Routine, Schedule

BUTTON_BOX_WIDTH = "15%"


class ScheduleSetter(remi.gui.HBox):
    """A component that offers controls to configure a Schedule object."""

    trashed: bool = False

    def __init__(self, schedule: Schedule):
        remi.gui.HBox.__init__(self)

        self.schedule: Schedule = schedule

        # hour buttons
        self.hour_buttons = remi.gui.HBox(
            height="100%", width=BUTTON_BOX_WIDTH
        )
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
        self.minute_buttons = remi.gui.HBox(
            height="100%", width=BUTTON_BOX_WIDTH
        )
        self.append(self.minute_buttons, "minute_buttons")

        # minute plus button
        self.minute_plus_button = Button("+")
        self.minute_plus_button.onclick.connect(self.on_minute_plus)
        self.minute_buttons.append(
            self.minute_plus_button, "minute_plus_button"
        )

        # minute minus button
        self.minute_minus_button = Button("-")
        self.minute_minus_button.onclick.connect(self.on_minute_minus)
        self.minute_buttons.append(
            self.minute_minus_button, "minute_minus_button"
        )

        # is on label
        self.is_on_label = CenteredLabel("Is On:")
        self.append(self.is_on_label, "is_on_label")

        # is on checkbox
        self.is_on_checkbox = remi.gui.CheckBox(checked=self.schedule.is_on)
        self.is_on_checkbox.onchange.connect(self.on_is_on_checkbox)
        self.append(self.is_on_checkbox, "is_on_checkbox")

        # trash button
        self.trash_button = TrashButton()
        self.trash_button.onclick.connect(self.on_trash_button)
        self.append(self.trash_button, "on_trash_button")

    def update_alarm_time_label(self):
        self.time_label.set_text(
            f"{self.schedule.hour:02d}:{self.schedule.minute:02d}"
        )

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
        self.schedule.is_on = is_checked

    def on_trash_button(self, _):
        self.trashed = True


class RoutineScheduler(remi.gui.VBox):
    routine: Routine

    def __init__(self, routine: Routine):
        remi.gui.VBox.__init__(self, width="100%")
        self.routine = routine

        self.schedule_setters = [
            ScheduleSetter(schedule) for schedule in self.routine.schedules
        ]
        self.schedule_setter_labels = [
            CenteredLabel(f"Schedule {i + 1}:")
            for i in range(len(self.schedule_setters))
        ]

        # schedule_setters grid
        self.schedule_setters_grid = remi.gui.GridBox(width="100%")
        self.append(self.schedule_setters_grid, "schedule_setters_grid")
        self.update_schedule_setters_grid()

        # add schedule button
        self.add_schedule_button = Button("Add Schedule")
        self.add_schedule_button.onclick.connect(self.on_add_schedule)
        self.append(self.add_schedule_button, "add_schedule_button")

    def on_add_schedule(self, widget):
        """add a new schedule to the routine"""
        self.routine.schedules.append(Schedule())
        self.schedule_setters.append(
            ScheduleSetter(self.routine.schedules[-1])
        )
        self.schedule_setter_labels.append(
            CenteredLabel(f"Schedule {len(self.routine.schedules)}:")
        )
        self.update_schedule_setters_grid()

    def thoroughly_delete_schedule(
        self,
        schedule_setter_label: CenteredLabel,
        schedule_setter: ScheduleSetter,
    ):
        """
        Thoroughly deletes a schedule object from the app and database
        """
        # remove from class lists
        self.schedule_setter_labels.remove(schedule_setter_label)
        self.schedule_setters.remove(schedule_setter)

        # remove from routine
        self.routine.schedules.remove(schedule_setter.schedule)

    def idle(self):
        """called every update_interval seconds"""
        self.check_and_clean_up_trashed_schedules()

    def check_and_clean_up_trashed_schedules(self):
        """if any of the schedule_setters have been trashed, remove them"""
        should_update_grid = False
        for schedule_setter_label, schedule_setter in zip(
            self.schedule_setter_labels, self.schedule_setters
        ):
            if schedule_setter.trashed:
                self.thoroughly_delete_schedule(
                    schedule_setter_label, schedule_setter
                )
                should_update_grid = True
        if should_update_grid:
            self.update_schedule_setters_grid()

    def update_schedule_setters_grid(self):
        """update the schedule_setters grid"""
        self.schedule_setters_grid.empty()

        grid_definition = [
            [f"schedule_setter_label_{i}", f"schedule_setter_{i}"]
            for i in range(len(self.schedule_setters))
        ]

        self.schedule_setters_grid.define_grid(grid_definition)
        self.schedule_setters_grid.set_column_sizes(["30%", "70%"])
        # this makes the rows the same height for each schedule_setter
        self.schedule_setters_grid.set_style(
            {
                "grid-template-rows": " ".join(
                    ["40px" for _ in self.schedule_setters]
                )
            }
        )

        for i, (schedule_label, schedule_setter) in enumerate(
            zip(self.schedule_setter_labels, self.schedule_setters)
        ):
            self.schedule_setters_grid.append(
                schedule_label, f"schedule_setter_label_{i}"
            )
            self.schedule_setters_grid.append(
                schedule_setter, f"schedule_setter_{i}"
            )
