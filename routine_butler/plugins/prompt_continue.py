from nicegui import ui
from pydantic import BaseModel


class PromptContinueGui(ui.card):
    def __init__(self, read_affirmation: "PromptContinue"):
        super().__init__()

        with self:
            ui.markdown(f"# {read_affirmation.prompt}")
            self.confirmation_button = ui.button("Success")
            self.confirmation_button.set_visibility(False)
            ui.timer(
                read_affirmation.wait_seconds,
                lambda: self.confirmation_button.set_visibility(True),
                once=True,
            )


class PromptContinue(BaseModel):
    prompt: str = "Do the thing!"
    wait_seconds: int = 5

    def administer(self, on_complete: callable):
        gui = PromptContinueGui(self)
        gui.confirmation_button.on("click", on_complete)
