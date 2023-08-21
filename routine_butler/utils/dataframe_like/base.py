from typing import Any, List, Protocol, Tuple


class DataframeLike(Protocol):
    """Protocol for interacting with a dataframe-like object"""

    def __init__(self, path: str):
        ...

    def get_row_at_idx(self, idx: int) -> List[Any]:
        """Returns the row at the given index as a dictionary of column names to
        values."""
        ...

    def get_all_data() -> List[List[Any]]:
        """Returns all data as a list of lists."""
        ...

    def shape(self) -> Tuple[int, int]:
        """Returns the number of rows and columns."""
        ...
