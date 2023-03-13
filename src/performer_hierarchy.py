from typing import Dict, Type

from performers.performer import Performer
from performers.header import Header
from performers.conditional_performer import ConditionalPerformer

PerformerTypeHierarchy = Dict[Type[Performer], "PerformerTypeHierarchy"]
PerformerHierarchy = Dict[Performer, "PerformerHierarchy"]

PERFORMER_TYPE_HIERARCHY = {Header: {}, ConditionalPerformer: {}}
