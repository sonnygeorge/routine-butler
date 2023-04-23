from nicegui import ui

from routine_butler.model.model import User

DRAWER_WIDTH = "300"
DRAWER_BREAKPOINT = "0"
V_SPACE = 4

class ProgramsSidebar(ui.right_drawer):
    def __init__(self, user: User):
        self.user = user

        super().__init__()
        self.classes(f"space-y-{V_SPACE} text-center py-0")
        self.props(
            f"breakpoint={DRAWER_BREAKPOINT} width={DRAWER_WIDTH} bordered"
        )

        with self:
            self.programs_frame = ui.element("div")
            with self.programs_frame:
                pass  # TODO

            ui.separator()

            # add program button
            add_program_button = ui.button("Add Program")
            add_program_button.on("click", self.add_program)

    def add_program(self):
        with self.programs_frame:
            pass  # TODO
