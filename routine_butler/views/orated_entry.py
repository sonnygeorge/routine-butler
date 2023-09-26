import asyncio
import json
import time
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from multiprocessing import Manager, Queue
from typing import Any, Callable, List, Protocol, TypedDict
import threading

import pyaudio
from loguru import logger
from nicegui import globals, ui
from vosk import KaldiRecognizer, Model

from routine_butler.globals import ICON_STRS, PagePath
from routine_butler.state import state
from routine_butler.utils.misc import initialize_page
from rpunct.rpunct import RestorePuncts

# TODO:

# 1. Mitigate how hx711 import is taking a long time
# 2. Ascertain disabling of buttons across states:
#   - Why isn't finish button disabling?
#   - Disable when page is loading for first time...
# 3. Cycle bar
# 4. Test when clicking finish right after stop
# 5. Catch EOF error at the end of transcribe's lifespan


###############################################
####### TEMP CODE FOR PROCESS DEBUGGING #######
###############################################


import psutil


def print_process_tree(pid=None, indent=0):
    """
    Print a tree of subprocesses for a given process ID.
    If no PID is provided, it defaults to the current process.
    """
    if pid is None:
        pid = psutil.Process().pid

    process = psutil.Process(pid)
    print(" " * indent + f"|- {process.name()} ({process.pid})")

    for child in process.children():
        print_process_tree(child.pid, indent + 4)


#########################################################################
####### TEMP CODE UNTIL NICEGUI RELEASES NEW VERSION W RUN MODULE #######
#########################################################################


process_pool = ProcessPoolExecutor()


async def _run(
    executor: Any, callback: Callable, *args: Any, **kwargs: Any
) -> Any:
    if globals.state == globals.State.STOPPING:
        return
    try:
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            executor, partial(callback, *args, **kwargs)
        )
        return result
    except RuntimeError as e:
        if "cannot schedule new futures after shutdown" not in str(e):
            raise
    except asyncio.exceptions.CancelledError:
        pass


async def cpu_bound(callback: Callable, *args: Any, **kwargs: Any) -> Any:
    """Run a CPU-bound function in a separate process."""
    return await _run(process_pool, callback, *args, **kwargs)


#########################################################################
#########################################################################


CHANNELS = 1
FRAME_RATE = 16000
RECORDING_CYCLE_SECONDS = 7
AUDIO_FORMAT = pyaudio.paInt16
FRAMES_PER_BUFFER = 3200
CHANNELS = 1
RATE = 16000
CHUNK = 1024
MIN_CHARS_PER_CYCLE = 6


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


def record(lock, signals: Signals, recorded: Queue, **kwargs):
    def should_record() -> bool:
        return (
            not signals["asr_is_paused"]
            and signals["transcription_model_is_loaded"]
        )

    def recording_cycle_is_complete(frames: list) -> bool:
        return len(frames) >= (FRAME_RATE * RECORDING_CYCLE_SECONDS) / CHUNK

    print(
        f"🚪 Entered Record | __name__: {__name__} | pid: {psutil.Process().pid}"
    )

    _transcribe = partial(transcribe, lock=lock, signals=signals, recorded=recorded, **kwargs)
    _punctuate = partial(punctuate, lock=lock, signals=signals, **kwargs)
    transcribe_thread = threading.Thread(target=_transcribe)
    punctuate_thread = threading.Thread(target=_punctuate)
    transcribe_thread.start()
    punctuate_thread.start()

    p = pyaudio.PyAudio()
    stream = p.open(
        format=AUDIO_FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=FRAMES_PER_BUFFER,
    )
    signals["stream_is_open"] = True
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

    print(
        f"🚪 Entered Transcribe | __name__: {__name__} | pid: {psutil.Process().pid}"
    )
    model = Model(None, "vosk-model-small-en-us-0.15")
    speech_recognizer = KaldiRecognizer(model, FRAME_RATE)
    speech_recognizer.SetWords(True)
    signals["transcription_model_is_loaded"] = True
    while not signals["asr_is_complete"]:
        if not should_transcribe():
            time.sleep(0.1)
            continue
        recording_cycle_frames = recorded.get()
        speech_recognizer.AcceptWaveform(b"".join(recording_cycle_frames))
        result = speech_recognizer.Result()
        text = json.loads(result)["text"]
        if len(text) < MIN_CHARS_PER_CYCLE:
            continue
        with lock:
            transcribed.put(text)
            transcribed_diary.append(text)


def punctuate(
    lock,
    signals: Signals,
    transcribed: Queue,
    transcribed_diary: List[str],
    punctuated_diary: List[str],
    **_,
):
    def check_if_punctuation_has_completed_and_update_signal():
        # print("��� CHECKING IF PUNCTUATION HAS COMPLETED")
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

    print(
        f"🚪 Entered Punctuate | __name__: {__name__} | pid: {psutil.Process().pid}"
    )
    rpunct = RestorePuncts()
    while not signals["punctuation_is_complete"]:
        if len(transcribed_diary) == 0:
            time.sleep(0.1)
            continue
        if not transcribed.empty():
            text_to_punctuate = transcribed.get()
            if text_to_punctuate in transcribed_diary:
                print(f"🔥 Punctuating... (more subprocesses should spawn)")
                punctuated_text = rpunct.punctuate(text_to_punctuate, lang="en")
                with lock:
                    punctuated_diary.append(punctuated_text)
        check_if_punctuation_has_completed_and_update_signal()


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


class ASR:
    SIDEBAR_WIDTH = 32
    SIDEBAR_HEIGHT_PX = 160
    ENTRY_BOX_WIDTH_PX = 500
    MIN_CHARS_PER_ENTRY = 30
    STATES: List[GUIState] = [
        FinalReviewState(),
        RecordingState(),
        ReadyState(),
        LoadingState(),
    ]

    def __init__(self):
        self.signals, self.queues, self.diaries = None, None, None
        self.state = None

        ui.timer(0.1, self.spawn_subprocesses, once=True)
        self.monitoring = ui.timer(0.4, self.monitor)
        self.should_activate_progress_bar = False
        self.n_transcriptions_as_of_last_check = 0
        self.inititalize_ui()

    def inititalize_ui(self):
        parent_container = ui.row()
        with parent_container:
            buttons_column = ui.column().classes("justify-around gap-0")
        buttons_column.style(f"height: {self.SIDEBAR_HEIGHT_PX}px;")
        with buttons_column.classes("bg-gray-300 rounded-lg shadow-md px-2"):
            self.undo_button = ui.button("Undo", icon="undo")
            self.undo_button.props(f"color=primary")
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
            with ui.column().style(f"width: {self.ENTRY_BOX_WIDTH_PX}px;"):
                self.text_area = ui.textarea(placeholder="Begin your entry...")
                self.text_area.disable()
                self.text_area.props("hide-bottom-space")
                self.text_area.classes("w-full h-full")
                self.progress_bar_frame = ui.element("div")
                # self.introduce_fresh_progress_bar()

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
        await cpu_bound(partialize(record))
        print("⬅️🚪 Yay! ASR subprocess finished!")

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
            for state in self.STATES:
                if state.should_enter(self.signals) and self.state != state:
                    logger.warning(f"Entering state: {state}")
                    self.update_state(state)
                    break

    def update_state(self, state: GUIState):
        self.finish_button.disable()
        self.state = state
        self.action_button.set_text(self.state.text)
        self.action_button.props(f"icon={self.state.icon}")
        self.action_button.props(f"color={self.state.color}")
        if self.state.should_disable_undo_button:
            self.undo_button.disable()
        else:
            self.undo_button.enable()
        if self.state.should_disable_finish_button:
            self.finish_button.disable()
        else:
            self.finish_button.enable()
        if self.state.should_disable_action_button:
            self.finish_button.disable()
        else:
            self.finish_button.enable()
        if isinstance(self.state, FinalReviewState):
            self.update_text_area()
            self.text_area.enable()
            self.manager.shutdown()
            self.monitoring.deactivate()

    def hdl_action_button_click(self):
        if isinstance(self.state, ReadyState):
            with self.lock:
                self.signals["asr_is_paused"] = False
            # self.should_activate_progress_bar = True
        elif isinstance(self.state, RecordingState):
            with self.lock:
                self.signals["asr_is_paused"] = True
            # self.should_activate_progress_bar = False
        elif isinstance(self.state, FinalReviewState):
            logger.warning("ASR COMPLETE (EXIT CONDITION)")  # FIXME
            ui.open(PagePath.HOME)

    def hdl_undo_button_click(self):
        if len(self.transcribed_diary) != 0:
            text_to_prune = self.transcribed_diary[-1]
            idx_to_prune = self.transcribed_diary.index(text_to_prune)
            self.transcribed_diary.pop(idx_to_prune)
            if len(self.punctuated_diary) > idx_to_prune:
                self.punctuated_diary.pop(idx_to_prune)
            self.update_text_area()

    def hdl_finish_button_click(self):
        with self.lock:
            self.signals["asr_is_complete"] = True


@ui.page(path=PagePath.ORATED_ENTRY)
def orated_entry():
    initialize_page(PagePath.ORATED_ENTRY, state=state)

    # Temporary code 
    pid = psutil.Process().pid
    ui.timer(
        5,
        lambda: print_process_tree(pid),
    )
    ASR()
