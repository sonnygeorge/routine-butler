import json
import re
import threading
import time
from functools import partial
from multiprocessing import Manager, Queue
from typing import List

import pyaudio
from loguru import logger
from nicegui import run, ui
from vosk import KaldiRecognizer, Model

from routine_butler.components import micro
from routine_butler.globals import ICON_STRS, PagePath
from routine_butler.plugins._orated_entry import (
    DEFAULT_SIGNALS,
    FinalReviewState,
    GUIState,
    LoadingState,
    ReadyState,
    RecordingState,
    Signals,
    TimerBar,
)
from routine_butler.plugins.orated_entry import OratedEntryRunData
from routine_butler.state import state
from routine_butler.utils.misc import (
    initialize_page,
    log_errors,
    redirect_to_page,
)
from routine_butler.utils.punctuate import RestorePuncts

INPUT_DEVICE_NAME_PATTERN = re.compile(r"(?i)(\S*usb\S*|\S*webcam\S*)")
CHANNELS = 1
RECORDING_CYCLE_SECONDS = 7
AUDIO_FORMAT = pyaudio.paInt16
FRAMES_PER_BUFFER = 3200
CHANNELS = 1
SAMPLE_RATE = 48000
CHUNK = 1024
MIN_CHARS_PER_CYCLE = 6


@log_errors
def record(lock, signals: Signals, recorded: Queue, **kwargs):
    def should_record() -> bool:
        return (
            not signals["asr_is_paused"]
            and signals["transcription_model_is_loaded"]
        )

    def recording_cycle_is_complete(frames: list) -> bool:
        return len(frames) >= (SAMPLE_RATE * RECORDING_CYCLE_SECONDS) / CHUNK

    _transcribe = partial(
        transcribe, lock=lock, signals=signals, recorded=recorded, **kwargs
    )
    _punctuate = partial(punctuate, lock=lock, signals=signals, **kwargs)
    transcribe_thread = threading.Thread(target=_transcribe)
    punctuate_thread = threading.Thread(target=_punctuate)
    transcribe_thread.start()
    punctuate_thread.start()

    p = pyaudio.PyAudio()
    device_idx = None
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get("deviceCount")
    for i in range(0, numdevices):
        n_channels = p.get_device_info_by_host_api_device_index(0, i).get(
            "maxInputChannels"
        )
        if n_channels > 0:
            name = p.get_device_info_by_host_api_device_index(0, i).get("name")
            logger.info(f"Input Device id {i} - {name}")
            if INPUT_DEVICE_NAME_PATTERN.search(name) is not None:
                device_idx = i
                logger.info(f"Opting to use device - '{name}'")
                break

    if device_idx is None:
        logger.error(
            f"Unable to find device w/ '{INPUT_DEVICE_NAME_PATTERN}' in name"
        )
        device_idx = 0

    stream = p.open(
        format=AUDIO_FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER,
        input_device_index=device_idx,
    )
    signals["stream_is_open"] = True

    # Start reading stream and appending cycles to queue
    frames = []
    while not signals["asr_is_complete"]:
        if not should_record():
            time.sleep(0.1)
            continue
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
        if recording_cycle_is_complete(frames):
            recorded.put(frames.copy())
            frames = []
    stream.stop_stream()
    stream.close()
    p.terminate()

    transcribe_thread.join()
    punctuate_thread.join()


@log_errors
def transcribe(
    lock,
    signals: Signals,
    recorded: Queue,
    transcribed: Queue,
    transcribed_diary: List[str],
    **_,
):
    def should_transcribe():
        return not signals["asr_is_paused"]

    model = Model(None, "vosk-model-small-en-us-0.15")
    speech_recognizer = KaldiRecognizer(model, SAMPLE_RATE)
    speech_recognizer.SetWords(True)
    signals["transcription_model_is_loaded"] = True
    while not signals["asr_is_complete"]:
        if not should_transcribe():
            time.sleep(0.1)
            continue
        try:
            recording_cycle_frames = recorded.get()
        except EOFError:
            # multiprocessing.Queue.get() raises EOFError when the queue is
            # empty and the queue's sender has exited. This is a hacky way to
            # catch this error and exit the thread.
            break
        speech_recognizer.AcceptWaveform(b"".join(recording_cycle_frames))
        result = speech_recognizer.Result()
        text = json.loads(result)["text"]
        if len(text) < MIN_CHARS_PER_CYCLE:
            continue
        with lock:
            transcribed.put(text)
            transcribed_diary.append(text)


@log_errors
def punctuate(
    lock,
    signals: Signals,
    transcribed: Queue,
    transcribed_diary: List[str],
    punctuated_diary: List[str],
    **_,
):
    def check_if_punctuation_has_completed_and_update_signal():
        punctuation_has_caught_up = (
            len(transcribed_diary) <= len(punctuated_diary)
            and len(transcribed_diary) > 0
        )
        punctation_has_completed = (
            punctuation_has_caught_up and signals["asr_is_complete"]
        )
        if punctation_has_completed:
            with lock:
                signals["punctuation_is_complete"] = True

    rpunct = RestorePuncts()
    while not signals["punctuation_is_complete"]:
        if len(transcribed_diary) == 0:
            time.sleep(0.1)
            continue
        if not transcribed.empty():
            text_to_punctuate = transcribed.get()
            if text_to_punctuate in transcribed_diary:
                punctuated_text = rpunct.punctuate(text_to_punctuate)
                with lock:
                    punctuated_diary.append(punctuated_text)
        check_if_punctuation_has_completed_and_update_signal()


class ASR:
    SIDEBAR_WIDTH = 36
    SIDEBAR_HEIGHT_PX = 160
    TEXT_BOX_WIDTH_PX = 500
    MIN_CHARS_PER_ENTRY = 30
    STATES: List[GUIState] = [
        FinalReviewState(),
        RecordingState(),
        ReadyState(),
        LoadingState(),
    ]

    def __init__(self):
        self.signals, self.queues, self.diaries = None, None, None
        self._state = None
        self.build_ui()
        ui.timer(0.1, self.spawn_subprocesses, once=True)
        self.monitoring = ui.timer(0.4, self.monitor)
        self.n_transcriptions_as_of_last_check = 0

    def build_ui(self):
        parent_container = ui.row()
        with parent_container:
            buttons_column = ui.column().classes("justify-around gap-0")
        buttons_column.style(f"height: {self.SIDEBAR_HEIGHT_PX}px;")
        with buttons_column.classes("bg-gray-300 rounded-lg shadow-md px-2"):
            self.undo_button = ui.button("Undo", icon="undo")
            self.undo_button.props("color=primary")
            self.undo_button.classes(f"w-{self.SIDEBAR_WIDTH}")
            self.undo_button.on("click", self.hdl_undo_button_click)
            self.finish_button = ui.button("Finish", icon=ICON_STRS.check)
            self.finish_button.props("primary")
            self.finish_button.on("click", self.hdl_finish_button_click)
            self.finish_button.classes(f"w-{self.SIDEBAR_WIDTH}")
            self.action_button = ui.button("")
            self.action_button.on("click", self.hdl_action_button_click)
            self.action_button.classes(f"w-{self.SIDEBAR_WIDTH}")
        with parent_container:
            with ui.column().style(f"width: {self.TEXT_BOX_WIDTH_PX}px;"):
                self.text_area = micro.text_area(
                    placeholder="Begin your entry..."
                )
                self.text_area.disable()
                self.text_area.props("hide-bottom-space")
                self.text_area.classes("w-full h-full")
                self.timer_bar = TimerBar(
                    seconds=RECORDING_CYCLE_SECONDS,
                    height_px=8,
                    width_px=self.TEXT_BOX_WIDTH_PX,
                )
        self.update_state(LoadingState())

    async def spawn_subprocesses(self):
        def partialize(func) -> callable:
            return partial(
                func,
                lock=self.lock,
                signals=self.signals,
                recorded=recorded_queue,
                transcribed=transcribed_queue,
                transcribed_diary=self.transcribed_diary,
                punctuated_diary=self.punctuated_diary,
            )

        self.manager = Manager()
        self.lock = self.manager.Lock()
        self.signals = self.manager.dict(DEFAULT_SIGNALS)
        recorded_queue = self.manager.Queue()
        transcribed_queue = self.manager.Queue()
        self.transcribed_diary = self.manager.list()
        self.punctuated_diary = self.manager.list()
        await run.cpu_bound(partialize(record))

    def update_text_area(self):
        if not self.signals["punctuation_is_complete"]:
            text = " ".join(self.transcribed_diary)
        else:
            text = " ".join(self.punctuated_diary)
        self.text_area.set_value(text)

    async def monitor(self):
        if self.signals is not None:
            # Check if text area should be updated
            n_transcriptions = len(self.transcribed_diary)
            if n_transcriptions > self.n_transcriptions_as_of_last_check:
                self.update_text_area()
            self.n_transcriptions_as_of_last_check = n_transcriptions
            # Check if a new state should be entered
            for _state in self.STATES:
                if _state.should_enter(self.signals) and self._state != _state:
                    self.update_state(_state)
                    break

    def update_state(self, state: GUIState):
        self.finish_button.disable()
        self._state = state
        self.action_button.set_text(self._state.text)
        self.action_button.props(f"icon={self._state.icon}")
        self.action_button.props(f"color={self._state.color}")
        if self._state.should_disable_undo_button:
            self.undo_button.disable()
        else:
            self.undo_button.enable()

        if self._state.should_disable_finish_button:
            self.finish_button.disable()
        else:
            self.finish_button.enable()

        if self._state.should_disable_action_button:
            self.action_button.disable()
        else:
            self.action_button.enable()
        # Start timer bar if entering recording state
        if isinstance(state, RecordingState):
            self.timer_bar.start()
        else:
            self.timer_bar.stop()
        # If entering final review state...
        if isinstance(state, FinalReviewState):
            self.update_text_area()
            self.text_area.enable()
            self.manager.shutdown()
            self.monitoring.deactivate()

    def hdl_action_button_click(self):
        if isinstance(self._state, ReadyState):
            with self.lock:
                self.signals["asr_is_paused"] = False
        elif isinstance(self._state, RecordingState):
            with self.lock:
                self.signals["asr_is_paused"] = True
        elif isinstance(self._state, FinalReviewState):
            run_data = OratedEntryRunData(entry=self.text_area.value)
            state.set_pending_run_data_to_be_added_to_db(run_data)
            state.set_is_pending_orated_entry(False)
            redirect_to_page(PagePath.DO_ROUTINE)

    def hdl_undo_button_click(self):
        if len(self.transcribed_diary) != 0:
            text_to_prune = self.transcribed_diary[-1]
            idx_to_prune = self.transcribed_diary.index(text_to_prune)
            self.transcribed_diary.pop(idx_to_prune)
            if len(self.punctuated_diary) > idx_to_prune:
                self.punctuated_diary.pop(idx_to_prune)
            self.update_text_area()

    def hdl_finish_button_click(self):
        if len(" ".join(self.transcribed_diary)) < self.MIN_CHARS_PER_ENTRY:
            ui.notify(f"Entry must be > {self.MIN_CHARS_PER_ENTRY} chars")
        else:
            with self.lock:
                self.signals["asr_is_complete"] = True


@ui.page(path=PagePath.ORATED_ENTRY)
def orated_entry():
    initialize_page(PagePath.ORATED_ENTRY, state=state)
    with micro.card().classes("absolute-center w-fit"):
        ASR()
