from typing import Callable, Optional, Union

from nicegui import ui


class IconExpansion(ui.expansion):
    def __init__(
        self,
        title: str,
        icon: Optional[Union[str, Callable]] = None,
        icon_kwargs: Optional[dict] = None,
        width: Optional[str] = None,
    ):
        """Custom element that creates an expansion with both a title and an icon in the
        header slot

        Args:
            title (str): title of the expansion
            icon (Optional[Union[str, Callable]], optional):
                either a:
                - string associated a nicegui icon
                - callable that returns a some nicegui element
                Defaults to None.
            icon_kwargs: optional kwargs to pass to the icon callable
            width: css width of the expansion
        """
        self.bordered_frame = ui.element("q-list").props("bordered")
        self.bordered_frame.classes("rounded-borders w-full")
        self.bordered_frame.style(f"width: {width};")
        with self.bordered_frame:
            super().__init__("")
            self.classes("w-full")

            with self.add_slot("header"):
                with ui.row().classes("justify-start items-center w-full"):
                    # add icon
                    if isinstance(icon, str):
                        ui.icon(icon).props("size=sm")
                    else:
                        icon(**icon_kwargs)
                    # add title
                    self.header_label = ui.label(title).classes("text-left")

            with self:
                # now, anything added to this object will come after this seperator
                ui.separator()
