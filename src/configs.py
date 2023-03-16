import rich.pretty
from loguru import logger


class Configs:
    # example
    content_width = "75%"

    def __init__(self):
        logger.debug(f"Created configs: {self.__str__()}")

    def __str__(self):
        _dict = {
            attr: getattr(self, attr)
            for attr in dir(self)
            if not callable(getattr(self, attr)) and not attr.startswith("__")
        }
        out = f"<class '{self.__class__.__module__}.{self.__class__.__name__}'>\n"
        out += rich.pretty.pretty_repr(_dict).replace("{\n", "").replace("\n}", "")
        return out


configs = Configs()
