import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String

from routine_butler.models.base import BaseDBORMModel, BaseDBPydanticModel


class ProgramRunORM(BaseDBORMModel):
    """BaseDBORMModel model for a Program Run"""

    __tablename__ = "program_runs"

    program_title = Column(String)
    plugin_type = Column(String)
    plugin_dict = Column(JSON)
    routine_title = Column(String)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    run_data = Column(JSON)
    user_uid = Column(Integer, ForeignKey("users.uid"))


class ProgramRun(BaseDBPydanticModel):
    """BaseDBPydanticModel model for a Program Run"""

    program_title: str
    plugin_type: str
    plugin_dict: dict
    routine_title: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    run_data: dict
    user_uid: int

    class Config:
        orm_model = ProgramRunORM
