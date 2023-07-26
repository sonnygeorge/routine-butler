import random
from dataclasses import dataclass
from enum import StrEnum
from typing import List, Optional

from loguru import logger
from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.configs import CLOUD_STORAGE_BUCKET, FLASHCARDS_FOLDER_NAME

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
        self.path_to_sheet: str = path_to_collection
        self.avg_seconds_per_card: int = int(fname.split("-")[-1])
        self.random_choice_weight: int = int(fname.split("-")[-2])
        self.name: str = "-".join(fname.split("-")[:-2])
        self.cached_cards: List[Flashcard] = []

    def __str__(self):
        return (
            f"🤖: {self.name} - 🏋️: {self.random_choice_weight} "
            f"- ⏱️: {self.avg_seconds_per_card}"
        )

    def cache_n_minutes_of_cards(self, n_minutes: int) -> None:
        # FIXME: implement
        self.cached_cards = [Flashcard("front", "back", self)]

    def get_random_card(self) -> Flashcard:
        return random.choice(self.cached_cards)


def get_collections_to_read(
    path: Optional[str] = None,
) -> List[str]:
    """Given the the path attribute of a flashcards program, return a list of the paths
    of sheets that should be read"""
    path_arg = None if path == "" else path
    try:
        items = CLOUD_STORAGE_BUCKET.list(path_arg)
    except ValueError:  # if list() raises ValueError...
        # ...the path is not a folder. We therefore assume it is a sheet.
        return [path]

    sheets_to_read = []
    for item in items:
        item_path = f"{path}/{item.name}" if path else item.name
        if item.is_dir:
            sheets_to_read.extend(get_collections_to_read(item_path))
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
        self.collections = self._get_collections(
            data.path, data.target_minutes
        )
        self.flashcards_queue: List[Flashcard] = self._get_flashcards_queue(
            data.target_minutes
        )
        self.current_card_idx = 0
        self.state = self.State.FRONT
        self.frame = micro.card().classes("flex flex-col items-center")
        self._update_ui()

    def _get_collections(
        self, path: str, target_minutes: int
    ) -> List[FlashcardCollection]:
        # Get paths of collections
        if path == "":
            path = FLASHCARDS_FOLDER_NAME
        else:
            path = f"{FLASHCARDS_FOLDER_NAME}/{path}"
        collection_paths = get_collections_to_read(path)
        # Parse collections
        collections: List[FlashcardCollection] = []
        for path in collection_paths:
            try:
                collections.append(FlashcardCollection(path))
            except Exception as e:
                logger.warning(
                    f"Couldn't parse flashcard collection: {path} - {e}"
                )
        logger.info(f"Found {len(collections)} flashcard collections")
        # Retrieve & cache cards for each collection
        for collection in collections:
            collection.cache_n_minutes_of_cards(target_minutes)
        return collections

    def _get_flashcards_queue(self, target_minutes: int) -> List[Flashcard]:
        _denom = sum([c.random_choice_weight for c in self.collections])
        PROBS = [c.random_choice_weight / _denom for c in self.collections]
        assert sum(PROBS) == 1

        _target_secs = target_minutes * 60
        _avg_secs = [c.avg_seconds_per_card for c in self.collections]
        _overall_avg_secs = sum([s * p for s, p in zip(_avg_secs, PROBS)])
        SECONDS_CAP = _target_secs - _overall_avg_secs

        queue: List[Flashcard] = []
        seconds_elapsed = 0
        while seconds_elapsed < SECONDS_CAP:
            collection = random.choices(self.collections, PROBS)[0]
            card = collection.get_random_card()
            queue.append(card)
            seconds_elapsed += int(collection.avg_seconds_per_card)
        return queue

    def _update_ui(self):
        fcard = self.flashcards_queue[self.current_card_idx]
        text = fcard.front if self.state == self.State.FRONT else fcard.back
        collection = str(fcard.collection)
        prog = f"Card {self.current_card_idx + 1}/{len(self.flashcards_queue)}"
        self.frame.clear()
        with self.frame:
            ui.label(prog).classes("font-xs")
            card = micro.card().style(f"width: {WIDTH}px; height: {HEIGHT}px")
            with card.classes("flex flex-col items-center justify-center"):
                ui.markdown(text)
            proceed_button = ui.button(self.state)
            ui.label(collection).classes("font-xs")
        proceed_button.on("click", self._hdl_button_click)

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
