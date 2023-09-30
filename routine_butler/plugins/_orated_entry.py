from typing import Protocol, TypedDict

from nicegui import ui

from routine_butler.globals import ICON_STRS


class Signals(TypedDict):
    stream_is_open: bool
    transcription_model_is_loaded: bool
    asr_is_paused: bool
    asr_is_complete: bool
    punctuation_is_complete: bool


DEFAULT_SIGNALS = Signals(
    stream_is_open=False,
    transcription_model_is_loaded=False,
    asr_is_paused=True,
    asr_is_complete=False,
    punctuation_is_complete=False,
)


class TimerBar(ui.element):
    def __init__(self, seconds: int, height_px: int, width_px: int):
        super().__init__("div")
        self.height_px = height_px
        self.width_px = width_px
        self.seconds = seconds
        self.current_progress_bar_tick = 1
        self.timer = None
        self._reset_bar()

    def _reset_bar(self):
        self.clear()
        size = f"{self.height_px}px"
        with self:
            self.bar = ui.linear_progress(0, size=size, show_value=False)
        self.bar.style(f"width: {self.width_px}px;")
        self.bar.classes("m-0 p-0")
        self.current_progress_bar_tick = 1

    def _update_bar(self):
        max_ticks = self.seconds - 2
        new_bar_value = self.current_progress_bar_tick / max_ticks
        self.bar.set_value(new_bar_value)
        if self.current_progress_bar_tick >= self.seconds:  # if cycle is over
            self._reset_bar()
        else:
            self.current_progress_bar_tick += 1

    def start(self):
        self.timer = ui.timer(1, self._update_bar)

    def stop(self):
        if self.timer is not None:
            self.timer.deactivate()
        self._reset_bar()


class GUIState(Protocol):
    text: str
    icon: str
    color: str
    should_disable_undo_button: bool
    should_disable_finish_button: bool
    should_disable_action_button: bool

    def should_enter(self, signals: Signals) -> bool:
        ...


class LoadingState:
    text = "Loading..."
    icon = ICON_STRS.loading
    color = "yellow"
    should_disable_undo_button = True
    should_disable_finish_button = True
    should_disable_action_button = True

    def should_enter(self, signals: Signals) -> bool:
        return (
            not signals["stream_is_open"]
            or not signals["transcription_model_is_loaded"]
        ) or (
            signals["asr_is_complete"]
            and not signals["punctuation_is_complete"]
        )


class ReadyState:
    text = "Start"
    icon = ICON_STRS.play
    color = "green"
    should_disable_undo_button = False
    should_disable_finish_button = False
    should_disable_action_button = False

    def should_enter(self, signals: Signals) -> bool:
        return (
            signals["stream_is_open"]
            and signals["transcription_model_is_loaded"]
            and signals["asr_is_paused"]
            and not signals["asr_is_complete"]
            and not signals["punctuation_is_complete"]
        )


class RecordingState:
    text = "Stop"
    icon = ICON_STRS.pause
    color = "red"
    should_disable_undo_button = True
    should_disable_finish_button = True
    should_disable_action_button = False

    def should_enter(self, signals: Signals) -> bool:
        return (
            signals["stream_is_open"]
            and signals["transcription_model_is_loaded"]
            and not signals["asr_is_paused"]
            and not signals["asr_is_complete"]
            and not signals["punctuation_is_complete"]
        )


class FinalReviewState:
    text = "Submit"
    icon = ICON_STRS.save
    color = "green"
    should_disable_undo_button = True
    should_disable_finish_button = True
    should_disable_action_button = False

    def should_enter(self, signals: Signals) -> bool:
        return signals["punctuation_is_complete"]
