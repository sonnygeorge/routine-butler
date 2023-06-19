import asyncio
import functools

from nicegui import ui

from routine_butler.components.header import Header
from routine_butler.constants import (
    ABS_ALARM_WAV_PATH,
    CONSTANT_RING_INTERVAL,
    PERIODIC_RING_INTERVAL,
    PagePath,
)
from routine_butler.models.routine import RingFrequency
from routine_butler.state import state
from routine_butler.utils import (
    apply_color_theme,
    play_wav_with_volume_adjustment,
    redirect_if_user_is_none,
    redirect_to_page,
    should_ring,
)

# FIXME: Implement snooze?
# FIXME: Cache pending routine & have a reboot bring user back to routine runner


async def async_play_wav_with_volume_adjustment(
    file_path: str, volume: float = 1.0
):
    await asyncio.sleep(0.2)  # give downtime for app loop to do its thing
    play_wav_with_volume_adjustment(file_path, volume)


@ui.page(path=PagePath.RING)
def ring():
    redirect_if_user_is_none(state.user)
    if state.next_alarm is None or not should_ring(state.next_alarm):
        redirect_to_page(PagePath.HOME)
    apply_color_theme()
    Header(hide_buttons=True)

    # Update state
    state.pending_routine_to_run = state.next_alarms_routine
    state.update_next_alarm()

    # Play the audio given the volume & ring frequency
    play_audio_callable = functools.partial(
        async_play_wav_with_volume_adjustment,
        ABS_ALARM_WAV_PATH,
        state.next_alarm.volume,
    )
    if state.next_alarm.ring_frequency == RingFrequency.CONSTANT:
        timer_interval = CONSTANT_RING_INTERVAL
    else:
        timer_interval = PERIODIC_RING_INTERVAL
    ui.timer(timer_interval, play_audio_callable)

    # Build the UI
    with ui.column().classes("absolute-center"):
        ui.label(f"Time for {state.pending_routine_to_run.title}!")
        begin_button = ui.button("Begin Routine")
        begin_button.on("click", lambda: redirect_to_page(PagePath.DO_ROUTINE))
