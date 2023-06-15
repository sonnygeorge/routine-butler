from nicegui import ui
from playsound import playsound

from routine_butler.components.header import Header
from routine_butler.constants import (
    ABS_MP3_PATH,
    CONSTANT_RING_INTERVAL,
    PERIODIC_RING_INTERVAL,
    PagePath,
)
from routine_butler.models.routine import RingFrequency
from routine_butler.state import state
from routine_butler.utils import (
    apply_color_theme,
    redirect_if_user_is_none,
    redirect_to_page,
    should_ring,
)


@ui.page(path=PagePath.RING)
def ring():
    redirect_if_user_is_none(state.user)
    if state.next_alarm is None or not should_ring(state.next_alarm):
        redirect_to_page(PagePath.HOME)
    apply_color_theme()
    Header(hide_buttons=True)

    # FIXME: Implement volume adjustment
    # FIXME: Implement snooze?
    # FIXME: Cache pending routine & have a reboot bring user back to routine runner

    interval = (
        CONSTANT_RING_INTERVAL
        if state.next_alarm.ring_frequency == RingFrequency.CONSTANT
        else PERIODIC_RING_INTERVAL
    )
    ui.timer(interval, lambda: playsound(ABS_MP3_PATH))

    state.pending_routine_to_run = state.next_alarms_routine
    state.update_next_alarm()

    with ui.column().classes("absolute-center"):
        ui.label(f"Time for {state.pending_routine_to_run.title}!")
        begin_button = ui.button("Begin Routine")
        begin_button.on("click", lambda: redirect_to_page(PagePath.DO_ROUTINE))
