import asyncio
import functools

from nicegui import ui

from routine_butler.configs import (
    ALARM_WAV_PATH,
    CONSTANT_RING_INTERVAL,
    PERIODIC_RING_INTERVAL,
    PagePath,
)
from routine_butler.hardware.audio import play_wav_with_volume_adjustment
from routine_butler.models import RingFrequency
from routine_butler.state import state
from routine_butler.utils.misc import initialize_page, redirect_to_page

# FIXME: Implement snooze?
# FIXME: Cache current routine & have a reboot bring user back to routine runner


async def async_play_wav_with_volume_adjustment(
    file_path: str, volume: float = 1.0
):
    await asyncio.sleep(0.2)  # give downtime for app loop to do its thing
    play_wav_with_volume_adjustment(file_path, volume)


def ring_next_alarm():
    """Does the steps associated with "ringing" the next alarm in the global state"""

    # Make the alarm's routine the pending routine in the global state
    state.current_routine = state.next_routine
    # Pre-initialize the asynchronous play-audio function with volume and file path
    play_audio_callable = functools.partial(
        async_play_wav_with_volume_adjustment,
        ALARM_WAV_PATH,
        state.next_alarm.volume,
    )
    # Establish the number of seconds between rings
    if state.next_alarm.ring_frequency == RingFrequency.CONSTANT:
        timer_interval = CONSTANT_RING_INTERVAL
    else:
        timer_interval = PERIODIC_RING_INTERVAL
    # Begin ringing the alarm (playing the audio on a loop)
    ui.timer(timer_interval, play_audio_callable)
    # Update the next alarm in the global state (removing the alarm being rang)
    state.update_next_alarm_and_next_routine()


@ui.page(path=PagePath.RING)
def ring():
    if state.next_alarm is None or not state.next_alarm.should_ring():
        redirect_to_page(PagePath.HOME)
        return

    initialize_page(page=PagePath.RING, state=state)

    ring_next_alarm()

    with ui.column().classes("absolute-center"):
        ui.label(f"Time for {state.current_routine.title}!")
        begin_button = ui.button("Begin Routine")
        begin_button.on("click", lambda: redirect_to_page(PagePath.DO_ROUTINE))
