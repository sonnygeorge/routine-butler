import re
from typing import TypedDict, Union

# Int is:
#  - Only numbers that do NOT start with 0 (protect padded number strings)
#  - Exactly 0
RE_INT = re.compile(r"(^[1-9]+\d*$|^0$)")

# Float is:
#  - Only numbers but with exactly 1 dot.
#  - The dot must always be followed number numbers
RE_FLOAT = re.compile(r"(^\d+\.\d+$|^\.\d+$)")

NUMERIC_VALIDATORS = {
    "Can't be empty": lambda v: v != "",
    "Must be numeric": lambda v: RE_INT.match(v) or RE_FLOAT.match(v),
}


class ConfidenceInterval(TypedDict):
    estimate: float
    lower_bound: float
    upper_bound: float
    confidence: float


class CheckRunData(TypedDict):
    reported_value: Union[bool, str, int, float, ConfidenceInterval]
