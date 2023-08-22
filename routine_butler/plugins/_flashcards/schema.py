import random
from dataclasses import dataclass
from typing import List, Optional

from loguru import logger
from nicegui import ui

from routine_butler.globals import DATAFRAME_LIKE
from routine_butler.plugins._flashcards.calculations import (
    calculate_flashcard_selection_weight,
)

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
        self.dataframe_like = DATAFRAME_LIKE(path_to_collection)
        self.cached_cards: List[Flashcard] = []
        self._cached_probabilities: Optional[List[float]] = None

    def __str__(self):
        return (
            f"🤖: {self.name} - 🏋️: {self.random_choice_weight} "
            f"- ⏱️: {self.avg_seconds_per_card}"
        )

    async def cache_all_cards(self) -> None:
        for idx, row in enumerate(await self.dataframe_like.get_all_data()):
            if len(row) != 2 and len(row) != 5:
                msg = f"Row {idx} of {self.name} has {len(row)} columns"
                logger.warning(msg)
                ui.notify(msg, level="warning")
                continue
            elif len(row) == 5:
                metadata = FlashcardMetadata(
                    mastery=int(row[2]),
                    appetite=int(row[3]),
                    has_bad_formatting=bool(int(row[4])),
                )
            else:
                metadata = FlashcardMetadata()
            self.cached_cards.append(
                Flashcard(row[0], row[1], self, idx, metadata)
            )
        self._calculate_and_cache_probabilities()

    def _calculate_and_cache_probabilities(self) -> None:
        weights = []
        for flashcard in self.cached_cards:
            if flashcard.metadata.mastery is None:
                mastery = DEFAULT_MASTERY
            else:
                mastery = flashcard.metadata.mastery
            if flashcard.metadata.appetite is None:
                appetite = DEFAULT_APPETITE
            else:
                appetite = flashcard.metadata.appetite
            if flashcard.metadata.has_bad_formatting is None:
                has_bad_formatting = False
            else:
                has_bad_formatting = flashcard.metadata.has_bad_formatting
            weight = calculate_flashcard_selection_weight(
                mastery, appetite, has_bad_formatting
            )
            weights.append(weight)
        self._cached_probabilities = [w / sum(weights) for w in weights]
        print(self._cached_probabilities)

    def pick_a_card(self) -> Flashcard:
        return random.choices(self.cached_cards, self._cached_probabilities)[0]
