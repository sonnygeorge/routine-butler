from typing import Dict, Type

from subapps.subapp import SubApp
from subapps.conditional_subapp import ConditionalSubApp

PerformerHierarchy = Dict[SubApp, "PerformerHierarchy"]

PERFORMER_HIERARCHY = {ConditionalSubApp(name="conditional_performer"): {}}
