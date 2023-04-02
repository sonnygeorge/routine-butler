import rich.pretty


class PrettyStrMixin:
    """Base class for classes to inherit from to get a pretty __str__ method"""

    def __str__(self):
        _dict = {
            attr: getattr(self, attr)
            for attr in dir(self)
            if not callable(getattr(self, attr)) and not attr.startswith("__")
        }
        out = f"<class '{self.__class__.__module__}.{self.__class__.__name__}'>\n"
        out += (
            rich.pretty.pretty_repr(_dict)
            .replace("{\n", "")
            .replace("\n}", "")
        )
        return out
