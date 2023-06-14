from typing import Dict

from pydantic import BaseModel, conint

PriorityScore = conint(ge=0, le=100)


class ChannelScoringData(BaseModel):
    substring_priority_scores: Dict[str, PriorityScore]
    priority_score: PriorityScore


UserId = str

YoutubeQueueGenerationPreferences = dict[UserId, ChannelScoringData]


class Video(BaseModel):
    id: str
    user_id: str
    title: str
    description: str
    length_seconds: int
    days_since_upload: int
