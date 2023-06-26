from typing import Optional

from pydantic import constr
from sqlalchemy import JSON, Column, ForeignKey, Integer, String

from routine_butler.models.base import BaseDBORMModel, BaseDBPydanticModel
from routine_butler.state import state


class ProgramORM(BaseDBORMModel):
    """BaseDBORMModel model for a Program"""

    __tablename__ = "programs"

    TITLE_LENGTH_LIMIT = 60

    title = Column(String(TITLE_LENGTH_LIMIT))
    plugin_type = Column(String)
    plugin_dict = Column(JSON)
    user_uid = Column(Integer, ForeignKey("users.uid"))


class Program(BaseDBPydanticModel):
    """BaseDBPydanticModel model for a Program"""

    title: constr(max_length=ProgramORM.TITLE_LENGTH_LIMIT) = "New Program"
    # TODO: add dynamic Enum-style type hint?
    plugin_type: Optional[str] = None
    plugin_dict: Optional[dict] = None
    user_uid: Optional[int] = None

    class Config:
        orm_model = ProgramORM

    def administer(self, on_complete: callable):
        plugin = state.plugins[self.plugin_type](**self.plugin_dict)
        plugin.administer(on_complete=on_complete)
