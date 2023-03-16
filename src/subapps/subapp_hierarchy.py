from typing import Dict

from subapps.subapp import SubApp
from subapps.alarm import Alarm

SubAppHierarchy = Dict[SubApp, "SubAppHierarchy"]

SUBAPP_HIERARCHY = {Alarm(name="alarm"): {}}
