from abc import ABC, abstractmethod
from typing import Any, List, Tuple


class DataframeLike(ABC):
    """ABC for interacting with a dataframe-like object"""

    def __init__(self, path: str):
        ...

    @abstractmethod
    def get_row_at_idx(self, idx: int) -> List[Any]:
        """Returns the row at the given index as a dictionary of column names to
        values."""
        ...

    @abstractmethod
    def shape(self) -> Tuple[int, int]:
        """Returns the number of rows and columns."""
        ...
