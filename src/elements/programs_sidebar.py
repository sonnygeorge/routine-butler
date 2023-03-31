from nicegui import ui

from utils.constants import clrs

BUTTON_STYLE = "background-color: {clr} !important;"
DRAWER_WIDTH = "300"
DRAWER_BREAKPOINT = "0"


class ProgramsSidebar(ui.right_drawer):
    def __init__(self):
        super().__init__()
        self.classes("space-y-4 text-center")
        self.props(f"breakpoint={DRAWER_BREAKPOINT} width={DRAWER_WIDTH}")
        self.style(f"background-color: {clrs.beige}")

        with self:
            self.programs_frame = ui.element("div")
            with self.programs_frame:
                # for program in user.programs:
                #     add something to the ui
                pass

            ui.separator()
            # add program button
            add_program_button = ui.button("Add Program")
            add_program_button.on("click", self.add_program)
            style = BUTTON_STYLE.format(clr=clrs.dark_green)
            add_program_button.style(style)

    def add_program(self):
        with self.programs_frame:
            pass
