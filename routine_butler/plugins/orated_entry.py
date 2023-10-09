from typing import TypedDict

from pydantic import BaseModel

from routine_butler.globals import PagePath
from routine_butler.state import state
from routine_butler.utils.misc import redirect_to_page

ESTIMATED_TIME_IN_SECONDS = 2.5 * 60


class OratedEntryRunData(TypedDict):
    entry: str


class OratedEntry(BaseModel):
    def administer(self, on_complete: callable):
        state.set_is_pending_orated_entry(True)
        redirect_to_page(PagePath.ORATED_ENTRY, n_seconds_before_redirect=0.1)

    def estimate_duration_in_seconds(self) -> float:
        return ESTIMATED_TIME_IN_SECONDS
