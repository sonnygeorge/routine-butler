from typing import Protocol, runtime_checkable

from loguru import logger
import remi
import rich.pretty

from configs import configs


class SubAppContainer(remi.gui.VBox):
    def __init__(self) -> None:
        remi.gui.VBox.__init__(self)
        self.set_style({"box-shadow": "4px 4px 2px rgba(0, 0, 0, 0.2)"})
        self.css_height = "100.0px"
        self.css_width = configs.content_width
        self.css_border_width = "1px"
        self.css_border_color = "gray"
        self.css_border_style = "dashed"
        self.css_font_family = "Courier"


@runtime_checkable
class SubAppProtocol(Protocol):
    name: str
    container: remi.gui.Container

    def should_be_on_stage(self) -> bool:
        ...

    def do_stuff(self) -> None:
        ...


class SubApp:
    """Base class for subapps, all subapps should inherit from this class."""

    def __init__(self, name: str, container: remi.gui.Container):
        """Initializes the subapp."""
        self.name = name
        self.container = container
        if not isinstance(self, SubAppProtocol):
            raise TypeError("Sub app {self.name} does not implement SubAppProtocol")
        logger.debug(f'Created subapp "{self.name}": {self.__str__()}')

    def __str__(self) -> str:
        _dict = {
            attr: getattr(self, attr) for attr in dir(self) if not attr.startswith("__")
        }
        out = f"<class '{self.__class__.__module__}.{self.__class__.__name__}'>\n"
        out += rich.pretty.pretty_repr(_dict).replace("{\n", "").replace("\n}", "")
        return out
