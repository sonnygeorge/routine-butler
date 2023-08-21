import csv
import datetime
import json
import os

from routine_butler.globals import CURRENT_DIR_PATH
from routine_butler.plugins._youtube_queue.schema import (
    ChannelScoringData,
    QueueParams,
)

N_DAYS_RETAINED_WATCH_HISTORY: int = 90

_ABS_WATCHED_VIDEOS_CSV_FILE_PATH = os.path.join(
    CURRENT_DIR_PATH, "plugins/_youtube_queue/watched_videos.csv"
)
_ABS_QUEUE_GENERATION_PREFERENCES_PATH = os.path.join(
    CURRENT_DIR_PATH, "plugins/_youtube_queue/queue_params.json"
)


# QUEUE_PARAMS singleton for use throughout the plugin

with open(_ABS_QUEUE_GENERATION_PREFERENCES_PATH, "r") as f:
    _queue_params_dict: dict = json.load(f)

QUEUE_PARAMS: QueueParams = {
    user_id: ChannelScoringData.parse_obj(data)
    for user_id, data in _queue_params_dict.items()
}

# Functions that abstract away the details of interfacing with watch history


def get_watched_video_history() -> list[str]:
    if not os.path.exists(_ABS_WATCHED_VIDEOS_CSV_FILE_PATH):
        return []

    with open(_ABS_WATCHED_VIDEOS_CSV_FILE_PATH, "r") as file:
        reader = csv.DictReader(file)
        return [row["uid"] for row in reader]


def add_to_watched_video_history(video_ids: list[str]) -> None:
    today = datetime.date.today()
    if not os.path.exists(_ABS_WATCHED_VIDEOS_CSV_FILE_PATH):
        rows = []
    else:
        with open(_ABS_WATCHED_VIDEOS_CSV_FILE_PATH, "r") as file:
            reader = csv.DictReader(file)
            rows = [row for row in reader]

        # expunge aged-out rows
        threshold_date = today - datetime.timedelta(
            days=N_DAYS_RETAINED_WATCH_HISTORY
        )
        rows = [
            row
            for row in rows
            if datetime.date.fromisoformat(row["date"]) >= threshold_date
        ]

    rows.extend([{"uid": v, "date": today.isoformat()} for v in video_ids])

    with open(_ABS_WATCHED_VIDEOS_CSV_FILE_PATH, "w") as file:
        writer = csv.DictWriter(file, fieldnames=["uid", "date"])
        writer.writeheader()
        writer.writerows(rows)
