from nicegui import ui
from pydantic import BaseModel

from routine_butler.hardware import box


class UnlockBox(BaseModel):
    def administer(self, on_complete: callable):
        ui.label("Unlocking box...")
        ui.timer(0.1, box.unlock, once=True)
        ui.timer(2, on_complete, once=True)

    def estimate_duration_in_seconds(self) -> float:
        return 0  # Unlock box should never be skipped
