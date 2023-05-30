from functools import partial

from routine_butler.components.primitives import SVG
from routine_butler.constants import (
    ABS_PROGRAM_SVG_PATH,
    ABS_REWARD_SVG_PATH,
    ABS_ROUTINE_SVG_PATH,
)

program_svg = partial(SVG, ABS_PROGRAM_SVG_PATH)
reward_svg = partial(SVG, ABS_REWARD_SVG_PATH)
routine_svg = partial(SVG, ABS_ROUTINE_SVG_PATH)
