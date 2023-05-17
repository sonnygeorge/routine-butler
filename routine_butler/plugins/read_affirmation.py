from nicegui import ui
from pydantic import BaseModel


class ReadAffirmationGui(ui.card):
    SECONDS_PER_CHAR = 0.25

    def __init__(self, read_affirmation: "ReadAffirmation"):
        super().__init__()
        self.read_affirmation = read_affirmation

        with self:
            ui.label(
                f"Read this affirmation {str(read_affirmation.n_times)} "
                f"times: {read_affirmation.affirmation}"
            )
            confirmation_txt = (
                f"I read it {self.read_affirmation.n_times} times"
            )
            self.confirmation_button = ui.button(confirmation_txt)
            self.confirmation_button.set_visibility(False)
            ui.timer(
                self._calculate_wait_seconds(),
                lambda: self.confirmation_button.set_visibility(True),
                once=True,
            )

    def _calculate_wait_seconds(self):
        return (
            self.SECONDS_PER_CHAR
            * len(self.read_affirmation.affirmation)
            * self.read_affirmation.n_times
        )


class ReadAffirmation(BaseModel):
    affirmation: str = "I can do this!"
    n_times: int = 1

    def administer(self, on_complete: callable):
        gui = ReadAffirmationGui(self)
        gui.confirmation_button.on("click", on_complete)


# Quick test of this module in isolation
if __name__ in {"__main__", "__mp_main__"}:

    def test_handle_completion():
        ui.notify("completion of program successfully handled")

    affirmation = ReadAffirmation()
    affirmation.administer(on_complete=test_handle_completion)
    ui.run()
