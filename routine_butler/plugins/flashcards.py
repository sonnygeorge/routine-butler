from typing import List, Optional

from loguru import logger
from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.configs import CLOUD_STORAGE_BUCKET, FLASHCARDS_FOLDER_NAME


class FlashcardCollection:
    def __init__(self, path_to_collection: str):
        # "{name}-{random_choice_weight}-{avg_seconds_per_card}"
        fname = path_to_collection.split("/")[-1]
        self.path_to_sheet = path_to_collection
        self.avg_seconds_per_card = fname.split("-")[-1]
        self.random_choice_weight = fname.split("-")[-2]
        self.name = "-".join(fname.split("-")[:-2])


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
    def __init__(self, data: "Flashcards", on_complete: callable):
        # target_minutes = data.target_minutes
        self.on_complete = on_complete

        if data.path == "":
            path = FLASHCARDS_FOLDER_NAME
        else:
            path = f"{FLASHCARDS_FOLDER_NAME}/{data.path}"

        collection_paths = get_collections_to_read(path)

        self.collections: List[FlashcardCollection] = []
        for path in collection_paths:
            try:
                self.collections.append(FlashcardCollection(path))
            except Exception as e:
                logger.warning(
                    f"Couldn't parse flashcard collection: {path} - {e}"
                )

        with micro.card().classes("flex flex-col items-center"):
            ui.label(str([c.name for c in self.collections]))

    def _get_flashcards(self):
        pass


class Flashcards(BaseModel):
    target_minutes: int = 5
    path: str = ""

    def administer(self, on_complete: callable):
        FlashcardsGui(self, on_complete)
