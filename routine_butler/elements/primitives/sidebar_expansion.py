from typing import Callable, Optional, Union

from nicegui import ui


class SidebarExpansion(ui.expansion):
    def __init__(
        self,
        title: str,
        icon: Optional[Union[str, Callable]] = None,
        icon_kwargs: Optional[dict] = None,
    ):
        self.expansion_frame = ui.element("q-list").props("bordered")
        self.expansion_frame.classes("rounded-borders w-full")
        with self.expansion_frame:
            super().__init__("")
            self.classes("w-full")

            with self.add_slot("header"):
                with ui.row().classes("justify-start items-center w-full"):
                    if isinstance(icon, str):
                        ui.icon(icon).props("size=sm")
                    else:
                        icon(**icon_kwargs)
                    self.header_label = ui.label(title).classes("text-left")

            with self:
                ui.separator()
