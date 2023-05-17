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
    plugin = Column(String)
    plugin_config = Column(JSON)
    user_uid = Column(Integer, ForeignKey("users.uid"))


class Program(BaseDBPydanticModel):
    """BaseDBPydanticModel model for a Program"""

    title: constr(max_length=ProgramORM.TITLE_LENGTH_LIMIT) = "New Program"
    plugin: Optional[str] = None  # TODO: add dynamic Enum-style type hint?
    plugin_config: Optional[dict] = None
    user_uid: Optional[int] = None

    class Config:
        orm_model = ProgramORM

    def administer(self, on_complete: callable):
        plugin = state.plugins[self.plugin](**self.plugin_config)
        plugin.administer(on_complete=on_complete)
