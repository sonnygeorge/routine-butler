from nicegui import ui

from routine_butler.database.models import User

DRAWER_WIDTH = "300"
DRAWER_BREAKPOINT = "0"


class ProgramsSidebar(ui.right_drawer):
    def __init__(self, user: User):
        self.user = user

        super().__init__()
        self.classes("space-y-4 text-center")
        self.props(f"breakpoint={DRAWER_BREAKPOINT} width={DRAWER_WIDTH} bordered")

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

    def add_program(self):
        with self.programs_frame:
            pass
