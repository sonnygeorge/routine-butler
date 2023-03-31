from nicegui import ui

from utils.constants import clrs

BUTTON_STYLE = "background-color: {clr} !important;"
DRAWER_WIDTH = "300"
DRAWER_BREAKPOINT = "0"


class SchedulesConfigurer(ui.expansion):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RoutineItemsConfigurer(ui.expansion):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RoutineConfigurer(ui.expansion):
    def __init__(self, routine, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RoutinesSidebar(ui.left_drawer):
    def __init__(self):
        super().__init__()
        self.classes("space-y-4 text-center")
        self.props(f"breakpoint={DRAWER_BREAKPOINT} width={DRAWER_WIDTH}")
        self.style(f"background-color: {clrs.beige}")

        with self:
            self.routines_frame = ui.element("div")
            with self.routines_frame:
                # for routine in user.routines:
                #     RoutineConfigurer(routine)
                pass

            ui.separator()
            # add routine button
            add_routine_button = ui.button("Add Routine")
            add_routine_button.on("click", self.add_routine)
            style = BUTTON_STYLE.format(clr=clrs.dark_green)
            add_routine_button.style(style)

    def add_routine(self):
        with self.routines_frame:
            pass
