import asyncio
import random
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import List, Optional, Tuple

from loguru import logger
from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.globals import (
    DATAFRAME_LIKE,
    FLASHCARDS_FOLDER_NAME,
    STORAGE_BUCKET,
)

# from routine_butler.plugins._flashcards.calculations import (
#     get_n_to_cache,
#     get_threshold_probability,
# )
from routine_butler.utils.cloud_storage_bucket.base import (
    CloudStorageBucketItem,
)

# FIXME: Have mastery inversely correlate to probability of being chosen
# FIXME: Have appetite correlate to probability of being chosen
# FIXME: Have bad formatting make probability of being chosen 0


# TODO: Consider naming of dataframe-like, g_suite, cloud_storage_bucket, etc.
#   * cloud_storage_bucket -> storage_bucket?
#   * g_suite -> google?
#   * dataframe-like -> data-client? data-interface? data-source?
#   * configs.py -> globals.py?
#   * sheet vs. workbook vs. collection etc.
# TODO: Seperate this code into different files in _flashcards folder
# TODO: Remove repeated retry code in google api calls

## TODO: Move "state" to configs and call it STATE

WIDTH = 700
MAX_N_COLLECTIONS = 36
DEFAULT_MASTERY = 2
DEFAULT_APPETITE = 3


@dataclass
class FlashcardMetadata:
    mastery: Optional[int] = None  # 0-10
    appetite: Optional[int] = None  # 0-10 ("appetite" to review again soon)
    has_bad_formatting: Optional[bool] = None


@dataclass
class Flashcard:
    front: str
    back: str
    collection: "FlashcardCollection"
    collection_idx: int
    metadata: Optional[FlashcardMetadata] = None

    @property
    def row(self) -> List[str]:
        return [
            self.front,
            self.back,
            self.metadata.mastery,
            self.metadata.appetite,
            int(self.metadata.has_bad_formatting),
        ]

    async def update_source(self):
        await self.collection.dataframe_like.update_row_at_idx(
            self.collection_idx, self.row
        )


class FlashcardCollection:
    def __init__(self, path_to_collection: str):
        # title format: "{name}-{random_choice_weight}-{avg_seconds_per_card}"
        fname: str = path_to_collection.split("/")[-1]
        self.avg_seconds_per_card: int = int(fname.split("-")[-1])
        self.random_choice_weight: int = int(fname.split("-")[-2])
        self.name: str = "-".join(fname.split("-")[:-2])
        self.cached_cards: List[Flashcard] = []
        self.dataframe_like = DATAFRAME_LIKE(path_to_collection)

    def __str__(self):
        return (
            f"🤖: {self.name} - 🏋️: {self.random_choice_weight} "
            f"- ⏱️: {self.avg_seconds_per_card}"
        )

    async def cache_all_cards(self) -> None:
        for idx, row in enumerate(await self.dataframe_like.get_all_data()):
            if len(row) == 5:
                metadata = FlashcardMetadata(
                    mastery=int(row[2]),
                    appetite=int(row[3]),
                    has_bad_formatting=bool(int(row[4])),
                )
            else:
                metadata = FlashcardMetadata()
            if len(row) == 2:
                self.cached_cards.append(
                    Flashcard(row[0], row[1], self, idx, metadata=metadata)
                )
            else:
                msg = f"Row {idx} of {self.name} has {len(row)} columns"
                logger.warning(msg)
                ui.notify(msg, level="warning")

    def get_random_card(self) -> Flashcard:
        return random.choice(self.cached_cards)


async def get_paths_of_collections_to_load(
    path: Optional[str] = None,
) -> List[str]:
    """Given the the path attribute of a flashcards program, return a list of the paths
    of sheets that should be read"""
    path_arg = None if path == "" else path
    try:
        items: List[CloudStorageBucketItem] = await STORAGE_BUCKET.list(
            path_arg
        )
    except ValueError:  # if list() raises ValueError...
        # ...the path is not a folder. We therefore assume it is a sheet.
        return [path]

    sheets_to_read = []
    for item in items:
        item_path = f"{path}/{item.name}" if path else item.name
        if item.is_dir:
            collections = await get_paths_of_collections_to_load(item_path)
            sheets_to_read.extend(collections)
        else:
            sheets_to_read.append(item_path)
    return sheets_to_read


def ctrl_panel_slider(value) -> ui.slider:
    slider = ui.slider(min=0, max=10, value=value).props("dense")
    return slider.classes("w-32")


def ctrl_panel_label(text) -> ui.label:
    return ui.label(text).classes("text-xs text-gray-600").props("dense")


def ctrl_panel_switch(value) -> ui.switch:
    return ui.switch(value=value).props("dense")


class FlashcardsGui:
    class State(StrEnum):
        FRONT = "Show Answer"
        BACK = "Next Card"
        FINAL = "Finish"

    def __init__(self, data: "Flashcards", on_complete: callable):
        self.on_complete = on_complete
        self.collections: List[FlashcardCollection] = []
        self.flashcards_queue: List[Flashcard] = []
        self.n_collections = 0
        self.n_collections_inspected = 0
        self.n_collections_loaded = 0
        self.retrieval_has_completed = False
        ui.timer(
            0.1,
            lambda: self._get_flashcards_queue(data.path, data.target_minutes),
            once=True,
        )
        self.recurring_update = ui.timer(0.1, self._update_ui)
        self.start_time = time.time()
        self.current_card_idx = 0
        self.state = self.State.FRONT
        self.frame = micro.card().classes("flex flex-col items-center")
        with self.frame:
            ui.label("...")
        self.progress_label = ui.label("").classes("text-xs text-gray-400")

    def _generate_progress_str(self) -> str:
        progress_str = f"{self.n_collections_inspected}/"
        progress_str += f"{self.n_collections} collections inspected"
        progress_str += f" | {self.n_collections_loaded}/"
        progress_str += f"{self.n_collections} collections loaded | "
        progress_str += f"{int(time.time() - self.start_time)}s elapsed"
        return progress_str

    def add_controls_frame(self, data: FlashcardMetadata) -> Tuple[ui.element]:
        with ui.row().classes("justify-center justify-center"):
            ctrl_panel_label("Mastery:")
            self.mastery_sldr = ctrl_panel_slider(
                data.mastery or DEFAULT_MASTERY
            )
            ctrl_panel_label("Appetite:")
            self.appetite_sldr = ctrl_panel_slider(
                data.appetite or DEFAULT_APPETITE
            )
            ctrl_panel_label("Has bad formatting?")
            self.has_bad_formatting_switch = ctrl_panel_switch(
                data.has_bad_formatting or False
            )

    def _update_ui(self):
        if not self.retrieval_has_completed:
            self.progress_label.set_text(self._generate_progress_str())
            return
        self.recurring_update.deactivate()
        fcard = self.flashcards_queue[self.current_card_idx]
        text = fcard.front if self.state == self.State.FRONT else fcard.back
        collection = str(fcard.collection)
        prog = f"Card {self.current_card_idx + 1}/{len(self.flashcards_queue)}"
        self.frame.clear()
        with self.frame:
            ui.label(prog).classes("font-bold text-gray-700")
            card = micro.card().style(f"width: {WIDTH}px;")
            with card.classes("flex flex-col items-center justify-center"):
                ui.markdown(text)
            if self.state != self.State.FRONT:
                self.add_controls_frame(fcard.metadata)
            proceed_button = ui.button(self.state)
            proceed_button.on("click", self._hdl_proceed_button_click)
            ui.label(collection)

    async def _get_flashcards_queue(
        self, path: str, target_minutes: int
    ) -> List[FlashcardCollection]:
        ## Get paths of collections
        if path == "":
            path = FLASHCARDS_FOLDER_NAME
        else:
            path = f"{FLASHCARDS_FOLDER_NAME}/{path}"
        collection_paths = await get_paths_of_collections_to_load(path)
        collection_paths = sorted(
            collection_paths,
            key=lambda path: int(path.split("-")[-2]),
            reverse=True,
        )[:MAX_N_COLLECTIONS]

        ## Parse paths and create collections
        uninspected_collections: List[FlashcardCollection] = []
        for path in collection_paths:
            try:
                uninspected_collections.append(FlashcardCollection(path))
            except Exception as e:
                logger.warning(
                    f"Couldn't parse flashcard collection: {path} - {e}"
                )
        self.n_collections = len(uninspected_collections)
        await asyncio.sleep(0.1)

        ## Load (retrieve & cache cards for) each collection
        for collection_path in collection_paths:
            collection = FlashcardCollection(collection_path)
            await collection.cache_all_cards()
            self.collections.append(collection)
            await asyncio.sleep(0.1)

        ## Queue up cards
        _denom = sum([c.random_choice_weight for c in self.collections])
        PROBS = [c.random_choice_weight / _denom for c in self.collections]
        TARGET_SECONDS = target_minutes * 60
        _avg_secs = [c.avg_seconds_per_card for c in self.collections]
        _overall_avg_secs = sum([s * p for s, p in zip(_avg_secs, PROBS)])
        SECONDS_CAP = TARGET_SECONDS - _overall_avg_secs
        seconds_elapsed = 0
        while seconds_elapsed < SECONDS_CAP:
            collection = random.choices(self.collections, PROBS)[0]
            card = collection.get_random_card()
            self.flashcards_queue.append(card)
            await asyncio.sleep(0.1)
            seconds_elapsed += int(collection.avg_seconds_per_card)
        self.retrieval_has_completed = True

    def _ctrl_panel_values_differ(self) -> bool:
        old_metadata = self.flashcards_queue[self.current_card_idx].metadata
        mastery = old_metadata.mastery
        appetite = old_metadata.appetite
        has_bad_formatting = old_metadata.has_bad_formatting
        return (
            mastery != self.mastery_sldr.value
            or appetite != self.appetite_sldr.value
            or has_bad_formatting != self.has_bad_formatting_switch.value
        )

    async def _hdl_proceed_button_click(self):
        # Update flashcard metadata in dataframe-like as necessary
        if self.state != self.State.FRONT:
            if self._ctrl_panel_values_differ():
                flashcard = self.flashcards_queue[self.current_card_idx]
                flashcard.metadata.mastery = self.mastery_sldr.value
                flashcard.metadata.appetite = self.appetite_sldr.value
                flashcard.metadata.has_bad_formatting = (
                    self.has_bad_formatting_switch.value
                )
                try:
                    await flashcard.update_source()
                except Exception as e:
                    logger.warning(f"Couldn't update flashcard in source: {e}")
        # Advance state
        if self.state == self.State.FRONT:
            if self.current_card_idx == len(self.flashcards_queue) - 1:
                self.state = self.State.FINAL
            else:
                self.state = self.State.BACK
        elif self.state == self.State.BACK:
            self.current_card_idx += 1
            self.state = self.State.FRONT
        # Act on state
        elif self.state == self.State.FINAL:
            self.on_complete()
            return
        self._update_ui()


class Flashcards(BaseModel):
    target_minutes: int = 5
    path: str = ""

    def administer(self, on_complete: callable):
        FlashcardsGui(self, on_complete)
