from typing import Optional

from pydantic import constr
from sqlalchemy import Column, String, Integer, ForeignKey

from routine_butler.models.base import (
    BaseDBORMModel,
    BaseDBPydanticModel,
)


class ProgramORM(BaseDBORMModel):
    """BaseDBORMModel model for a Program"""

    __tablename__ = "programs"

    TITLE_LENGTH_LIMIT = 60

    title = Column(String(TITLE_LENGTH_LIMIT))
    user_uid = Column(Integer, ForeignKey("users.uid"))


class Program(BaseDBPydanticModel):
    """BaseDBPydanticModel model for a Program"""

    title: constr(max_length=ProgramORM.TITLE_LENGTH_LIMIT) = "New Program"
    user_uid: Optional[int] = None

    class Config:
        orm_model = ProgramORM
