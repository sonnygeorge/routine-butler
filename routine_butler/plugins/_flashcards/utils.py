from typing import List, Optional

from nicegui import ui

from routine_butler.globals import STORAGE_BUCKET
from routine_butler.utils.cloud_storage_bucket import CloudStorageBucketItem


def control_panel_slider(value) -> ui.slider:
    slider = ui.slider(min=0, max=10, value=value).props("dense")
    return slider.classes("w-32")


def control_panel_label(text) -> ui.label:
    return ui.label(text).classes("text-xs text-gray-600").props("dense")


def control_panel_switch(value) -> ui.switch:
    return ui.switch(value=value).props("dense")


async def get_paths_of_collections_to_load(
    path: Optional[str] = None,
) -> List[str]:
    """Given the the path attribute of a flashcards program, return a list of the paths
    of sheets that should be read"""
    if "-" in path:
        # It is a path to a single sheet
        return [path]

    path_arg = None if path == "" else path
    items: List[CloudStorageBucketItem] = await STORAGE_BUCKET.list(path_arg)
    sheets_to_read = []
    for item in items:
        item_path = f"{path}/{item.name}" if path else item.name
        if item.is_dir:
            collections = await get_paths_of_collections_to_load(item_path)
            sheets_to_read.extend(collections)
        else:
            sheets_to_read.append(item_path)
    return sheets_to_read
