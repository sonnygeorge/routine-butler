from typing import TypedDict

from pydantic import BaseModel

from routine_butler.globals import PagePath
from routine_butler.state import state
from routine_butler.utils.misc import redirect_to_page


class OratedEntryRunData(TypedDict):
    entry: str


class OratedEntry(BaseModel):
    def administer(self, on_complete: callable):
        state.set_is_pending_orated_entry(True)
        redirect_to_page(PagePath.ORATED_ENTRY, n_seconds_before_redirect=0.1)
