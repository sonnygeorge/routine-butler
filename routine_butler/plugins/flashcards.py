import asyncio
import random
import time
from enum import StrEnum
from typing import List, Tuple

from loguru import logger
from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.globals import FLASHCARDS_FOLDER_NAME
from routine_butler.plugins._flashcards.schema import (
    DEFAULT_APPETITE,
    DEFAULT_MASTERY,
    Flashcard,
    FlashcardCollection,
)
from routine_butler.plugins._flashcards.utils import (
    control_panel_label,
    control_panel_slider,
    control_panel_switch,
    get_paths_of_collections_to_load,
)

# TODO: Consider naming of dataframe-like, g_suite, cloud_storage_bucket, etc.
#   * cloud_storage_bucket -> storage_bucket?
#   * g_suite -> google?
#   * dataframe-like -> data-client? data-interface? data-source?
#   * configs.py -> globals.py?
#   * sheet vs. workbook vs. collection etc.

## TODO: Move "state" to configs and call it STATE

WIDTH = 700
MAX_N_COLLECTIONS = 36


class FlashcardsGui:
    class State(StrEnum):
        FRONT = "Show Answer"
        BACK = "Next Card"
        FINAL = "Finish"

    def __init__(self, data: "Flashcards", on_complete: callable):
        self.on_complete = on_complete
        self.target_minutes, self.path = data.target_minutes, data.path

        self.collection_paths: List[str] = []
        self.collections: List[FlashcardCollection] = []
        self.flashcards_queue: List[Flashcard] = []

        self.current_card_idx = 0
        self.state = self.State.FRONT
        self.queue_generation_has_completed = False

        self.start_time = time.time()
        ui.timer(0.1, self._get_flashcards_queue, once=True)
        self.recurring_update_while_awaiting_queue = ui.timer(
            0.1, self._update_ui
        )

        self.frame = micro.card().classes("flex flex-col items-center")
        with self.frame:
            ui.label("...")
        self.progress_label = ui.label("").classes("text-xs text-gray-400")

    @property
    def current_card(self) -> Flashcard:
        return self.flashcards_queue[self.current_card_idx]

    @property
    def target_seconds(self) -> int:
        return self.target_minutes * 60

    async def _get_flashcards_queue(self) -> List[FlashcardCollection]:
        # Get paths of collections
        if self.path == "":
            path = FLASHCARDS_FOLDER_NAME
        else:
            path = f"{FLASHCARDS_FOLDER_NAME}/{self.path}"
        self.collection_paths = await get_paths_of_collections_to_load(path)
        await asyncio.sleep(0.1)

        # Load (retrieve & cache cards for) each collection
        for collection_path in self.collection_paths:
            try:
                collection = FlashcardCollection(collection_path)
            except Exception as e:
                logger.warning(f"Couldn't parse: {collection_path}: {e}")
                continue
            await collection.cache_all_cards()
            self.collections.append(collection)
            await asyncio.sleep(0.1)

        # Sort by random_choice_weight and take the top MAX_N_COLLECTIONS
        self.collections = sorted(
            self.collections,
            key=lambda c: c.random_choice_weight,
            reverse=True,
        )[:MAX_N_COLLECTIONS]

        # Calculate the probability of each collection being chosen
        denom = sum([c.random_choice_weight for c in self.collections])
        probs = [c.random_choice_weight / denom for c in self.collections]

        # Calculate a seconds cap to use for cumulative study time
        avg_secs_list = [c.avg_seconds_per_card for c in self.collections]
        overall_avg_secs = sum([s * p for s, p in zip(avg_secs_list, probs)])
        SECONDS_CAP = self.target_seconds - overall_avg_secs

        # Choose a collection, pick a card, and queue it until the seconds cap is reached
        cumulative_seconds_of_studying = 0
        while cumulative_seconds_of_studying < SECONDS_CAP:
            collection = random.choices(self.collections, probs)[0]
            card = collection.pick_a_card()
            self.flashcards_queue.append(card)
            await asyncio.sleep(0.1)
            cumulative_seconds_of_studying += collection.avg_seconds_per_card
        self.queue_generation_has_completed = True

    def _generate_progress_str(self) -> str:
        progress_str = f"{len(self.collections)}/"
        progress_str += f"{len(self.collection_paths)} collections loaded | "
        progress_str += f"{int(time.time() - self.start_time)}s elapsed"
        return progress_str

    def _add_control_panel(self) -> Tuple[ui.element]:
        with ui.row().classes("justify-center justify-center"):
            control_panel_label("Mastery:")
            self.mastery_slider = control_panel_slider(
                self.current_card.metadata.mastery or DEFAULT_MASTERY
            )

            control_panel_label("Appetite:")
            self.appetite_slider = control_panel_slider(
                self.current_card.metadata.appetite or DEFAULT_APPETITE
            )

            control_panel_label("Has bad formatting?")
            self.has_bad_formatting_switch = control_panel_switch(
                self.current_card.metadata.has_bad_formatting or False
            )

    def _update_ui(self) -> None:
        if not self.queue_generation_has_completed:
            self.progress_label.set_text(self._generate_progress_str())
            return
        self.recurring_update_while_awaiting_queue.deactivate()

        if self.state == self.State.FRONT:
            flashcard_text = self.current_card.front
        else:
            flashcard_text = self.current_card.back

        self.frame.clear()
        with self.frame:
            # Progress label
            progress_label_str = (
                f"Card {self.current_card_idx + 1}/"
                f"{len(self.flashcards_queue)}"
            )
            ui.label(progress_label_str).classes("font-bold text-gray-700")
            # Flashcard
            card = micro.card().style(f"width: {WIDTH}px;")
            with card.classes("flex flex-col items-center justify-center"):
                micro.markdown(flashcard_text)
            # Control panel
            if self.state != self.State.FRONT:
                self._add_control_panel()
            # Proceed button
            proceed_button = ui.button(self.state)
            proceed_button.on("click", self.hdl_proceed_button_click)
            # Collection label
            ui.label(str(self.current_card.collection))

    def _metadata_was_changed_by_user(self) -> bool:
        old_mastery = (self.current_card.metadata.mastery,)
        old_appetite = (self.current_card.metadata.appetite,)
        old_has_bad_formatting = self.current_card.metadata.has_bad_formatting
        return (
            old_mastery != self.mastery_slider.value
            or old_appetite != self.appetite_slider.value
            or old_has_bad_formatting != self.has_bad_formatting_switch.value
        )

    def _update_current_flashcard_metadata_with_ui_values(self) -> None:
        self.current_card.metadata.mastery = self.mastery_slider.value
        self.current_card.metadata.appetite = self.appetite_slider.value
        self.current_card.metadata.has_bad_formatting = (
            self.has_bad_formatting_switch.value
        )

    async def hdl_proceed_button_click(self):
        # Update flashcard metadata in dataframe-like as necessary
        if self.state != self.State.FRONT:
            if self._metadata_was_changed_by_user():
                self._update_current_flashcard_metadata_with_ui_values()
                try:
                    await self.current_card.update_source()
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
