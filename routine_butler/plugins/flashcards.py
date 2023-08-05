import asyncio
import random
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import List, Optional

from loguru import logger
from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.globals import (
    DATAFRAME_LIKE,
    FLASHCARDS_FOLDER_NAME,
    STORAGE_BUCKET,
)
from routine_butler.plugins._flashcards.calculations import (
    get_n_to_cache,
    get_threshold_probability,
)

# TODO: Possible speedups:
#   * 1. Make shape() more efficient
#   * 2.
#     - change the dataframe-like interface to get consecutive rows idxs in one call
#     - modify the cache function to: pre-select the idxs it will retrieve, sort them
#       into ranges of consecutive idxs, and retrieve ranges instead of individual rows
#     - make sure this pre-selection is done without replacement to avoid
#       redundant calls

# TODO: Error handling for when more than two columns detected
# TODO: Figure out how to get google auth flow seamlessly into app
# TODO: Make height automatically size
# TODO: Change state/button strategy to have a flip button & a next button that
#       appears or becomes active after the flip button is clicked...
#       No need for "final" button / state hoo-hah
# TODO: Move "state" to configs and call it STATE
# TODO: Consider naming of dataframe-like, g_suite, cloud_storage_bucket, etc.
#   * cloud_storage_bucket -> storage_bucket?
#   * g_suite -> google?
#   * dataframe-like -> data-client? data-interface? data-source?
#   * configs.py -> globals.py?
#   * sheet vs. workbook vs. collection etc.
# TODO: seperate this code into different files in _flashcards folder
# TODO: Remove repeated retry code in google api calls

WIDTH = 700
HEIGHT = 370


@dataclass
class Flashcard:
    front: str
    back: str
    collection: "FlashcardCollection"


class FlashcardCollection:
    def __init__(self, path_to_collection: str):
        # "{name}-{random_choice_weight}-{avg_seconds_per_card}"
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

    async def cache_n_cards(self, n_to_cache: int, n_possible: int) -> None:
        n_to_cache = min(n_to_cache, n_possible)
        choosable_idxs = list(range(n_possible))
        for _ in range(n_to_cache):
            if len(choosable_idxs) == 0:
                break
            idx = random.choice(choosable_idxs)
            row = await self.dataframe_like.get_row_at_idx(idx)
            try:
                self.cached_cards.append(Flashcard(row[0], row[1], self))
            except IndexError:
                logger.warning(
                    f"Couldn't parse flashcard at idx: {idx} -- "
                    f"Expected 2 columns in sheet but got: {row}"
                )
            choosable_idxs.remove(idx)  # without replacement

    def get_random_card(self) -> Flashcard:
        return random.choice(self.cached_cards)


async def get_paths_of_collections_to_load(
    path: Optional[str] = None,
) -> List[str]:
    """Given the the path attribute of a flashcards program, return a list of the paths
    of sheets that should be read"""
    path_arg = None if path == "" else path
    try:
        items = await STORAGE_BUCKET.list(path_arg)
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


class FlashcardsGui:
    class State(StrEnum):
        FRONT = "Show Answer"
        BACK = "Next Card"
        FINAL = "Finish"

    def __init__(self, data: "Flashcards", on_complete: callable):
        self.on_complete = on_complete
        self.collections: List[FlashcardCollection] = []
        self.flashcards_queue: List[Flashcard] = []
        self.n_collections_found = 0
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
            ui.label("🐛🐜🐢...")
        self.progress_label = ui.label("").classes("text-xs text-gray-400")

    def _generate_progress_str(self) -> str:
        progress_str = f"{self.n_collections_inspected}/"
        progress_str += f"{self.n_collections_found} collections inspected"
        progress_str += f" | {self.n_collections_loaded}/"
        progress_str += f"{self.n_collections_found} collections loaded | "
        progress_str += f"{int(time.time() - self.start_time)}s elapsed"
        return progress_str

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
            ui.label(prog)
            card = micro.card().style(f"width: {WIDTH}px; height: {HEIGHT}px")
            with card.classes("flex flex-col items-center justify-center"):
                ui.markdown(text)
            proceed_button = ui.button(self.state)
            ui.label(collection)
        proceed_button.on("click", self._hdl_button_click)

    async def _get_flashcards_queue(
        self, path: str, target_minutes: int
    ) -> List[FlashcardCollection]:
        ## Get paths of collections
        if path == "":
            path = FLASHCARDS_FOLDER_NAME
        else:
            path = f"{FLASHCARDS_FOLDER_NAME}/{path}"
        collection_paths = await get_paths_of_collections_to_load(path)

        ## Parse paths and create collections
        uninspected_collections: List[FlashcardCollection] = []
        for path in collection_paths:
            try:
                uninspected_collections.append(FlashcardCollection(path))
            except Exception as e:
                logger.warning(
                    f"Couldn't parse flashcard collection: {path} - {e}"
                )
        self.n_collections_found = len(uninspected_collections)
        await asyncio.sleep(0.1)

        ## Inspect the shape of the dataframe of each collection and add to
        #  collections if it has a valid shape
        self.n_collections_inspected = 0
        N_CARDS_IN_COLLECTIONS = []
        for collection in uninspected_collections:
            n_rows, n_cols = await collection.dataframe_like.shape()
            if n_cols != 2:
                warning = f"Skipping collection '{collection.name}' because it"
                warning += f" has {n_cols} columns. Expected 2."
                logger.warning(warning)
                ui.notify(warning, icon="warning")
            else:
                self.collections.append(collection)
                N_CARDS_IN_COLLECTIONS.append(n_rows)
            self.n_collections_inspected += 1
            await asyncio.sleep(0.1)
        self.n_collections_found = len(self.collections)  # Update accordingly

        ## Load (retrieve & cache cards for) each collection
        _denom = sum([c.random_choice_weight for c in self.collections])
        PROBS = [c.random_choice_weight / _denom for c in self.collections]
        THRESHOLD_PROB = get_threshold_probability(self.n_collections_found)
        TARGET_SECONDS = target_minutes * 60
        self.n_collections_loaded = 0
        zipped = zip(self.collections, PROBS, N_CARDS_IN_COLLECTIONS)
        for collection, selection_prob, n_possible_cards in zipped:
            n_to_cache = get_n_to_cache(
                collection=collection,
                selection_probability=selection_prob,
                threshold_probability=THRESHOLD_PROB,
                target_seconds=TARGET_SECONDS,
            )
            await collection.cache_n_cards(n_to_cache, n_possible_cards)
            self.n_collections_loaded += 1
            await asyncio.sleep(0.1)

        ## Queue up cards
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

    def _hdl_button_click(self):
        if self.state == self.State.FRONT:
            if self.current_card_idx == len(self.flashcards_queue) - 1:
                self.state = self.State.FINAL
            else:
                self.state = self.State.BACK
        elif self.state == self.State.BACK:
            self.current_card_idx += 1
            self.state = self.State.FRONT
        elif self.state == self.State.FINAL:
            self.on_complete()
            return
        self._update_ui()


class Flashcards(BaseModel):
    target_minutes: int = 5
    path: str = ""

    def administer(self, on_complete: callable):
        FlashcardsGui(self, on_complete)
