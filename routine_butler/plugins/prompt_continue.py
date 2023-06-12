from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro


class PromptContinueGui:
    def __init__(self, data: "PromptContinue"):
        with micro.card():
            ui.markdown(f"# {data.prompt}")
            self.confirmation_button = ui.button("Success")
            self.confirmation_button.set_visibility(False)
            ui.timer(
                data.wait_seconds,
                lambda: self.confirmation_button.set_visibility(True),
                once=True,
            )


class PromptContinue(BaseModel):
    prompt: str = "Do the thing!"
    wait_seconds: int = 5

    def administer(self, on_complete: callable):
        gui = PromptContinueGui(self)
        gui.confirmation_button.on("click", on_complete)
