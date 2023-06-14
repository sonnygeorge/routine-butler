import json
import os
from typing import Dict

from pydantic import BaseModel, confloat

from routine_butler.constants import ABS_CURRENT_DIR


class Video(BaseModel):
    id: str
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

_ABS_QUEUE_GENERATION_PREFERENCES_PATH = os.path.join(
    ABS_CURRENT_DIR, "plugins/_youtube/queue_params.json"
)
with open(_ABS_QUEUE_GENERATION_PREFERENCES_PATH, "r") as f:
    _queue_params_dict: dict = json.load(f)

QUEUE_PARAMS: QueueParams = {
    user_id: ChannelScoringData.parse_obj(data)
    for user_id, data in _queue_params_dict.items()
}
