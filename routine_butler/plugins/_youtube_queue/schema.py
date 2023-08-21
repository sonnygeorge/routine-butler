from typing import Dict

from pydantic import BaseModel, confloat


class Video(BaseModel):
    uid: str
    user_id: str
    title: str
    description: str
    length_seconds: int
    days_since_upload: int


PriorityScore = confloat(ge=0.0, le=100.0)


class ChannelScoringData(BaseModel):
    substring_priority_scores: Dict[str, PriorityScore]
    priority_score: PriorityScore


UserId = str
QueueParams = dict[UserId, ChannelScoringData]
