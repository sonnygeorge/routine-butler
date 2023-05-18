from typing import TYPE_CHECKING, Dict, List, Optional, Type

from sqlalchemy.engine import Engine

from routine_butler.models.routine import Routine
from routine_butler.utils import ProgramPlugin, dynamically_get_plugins

if TYPE_CHECKING:
    from routine_butler.models.program import Program
    from routine_butler.models.user import User


class State:
    engine: Engine = None
    user: "User" = None
    programs: List["Program"] = []
    program_titles: List[str] = []
    plugin_types: Dict[str, Type[ProgramPlugin]] = {}
    pending_routine_to_run: Optional[Routine] = None

    def set_user(self, user: "User"):
        self.user = user
        self.plugin_types = dynamically_get_plugins()
        self.update_programs()

    def update_programs(self):
        self.programs = [p for p in self.user.get_programs(self.engine)]
        self.program_titles = [p.title for p in self.programs]


state = State()  # instantiate singleton for the app to import
