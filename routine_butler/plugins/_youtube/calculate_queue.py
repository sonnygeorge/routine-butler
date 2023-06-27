from typing import List, Tuple

from routine_butler.plugins._youtube.schema import Video
from routine_butler.plugins._youtube.utils import QUEUE_PARAMS, QueueParams

N_QUEUE_VIDEOS_SAFETY_LIMIT = 100

DURATION_SECONDS_SCORE_MULTIPLIERS = [
    (0, 1.0),  # 0-1 minutes
    (5 * 60, 0.92),  # 5-9 minutes
    (10 * 60, 0.83),  # 10-14 minutes
    (15 * 60, 0.67),  # 15+ minutes
]
DAYS_SINCE_UPLOAD_SCORE_MULTIPLIERS = [
    (0, 1.0),  # 0-1 days ago
    (2, 0.9),  # 2-3 days ago
    (4, 0.8),  # 4-6 days ago
    (7, 0.5),  # 7-29 days ago
    (30, 0.3),  # 30-179 days ago
    (180, 0.1),  # 180+ days ago
]
ALLOWED_TARGET_DURATION_SECONDS_OVERSHOOT_AMOUNTS = [
    (0, 3.4 * 60),  # 0-1.5 minutes can overshoot by up to 3.4 minutes
    (1.5 * 60, 2.8 * 60),  # 1.5-3 minutes can overshoot by up to 2.8 minutes
    (5 * 60, 2.3 * 60),  # 5-10 minutes can overshoot by up to 2.3 minutes
    (10 * 60, 1.5 * 60),  # 10-20 minutes can overshoot by up to 1.5 minutes
]


def calculate_max_duration_from_target_duration_seconds(
    target_duration: int,
) -> float:
    """Takes a target duration in seconds and returns the maximum allowed duration for
    the queue."""
    ALLOWED_TARGET_DURATION_SECONDS_OVERSHOOT_AMOUNTS.sort(
        key=lambda x: x[0], reverse=True
    )
    for (
        target_duration_seconds,
        overshoot_amount,
    ) in ALLOWED_TARGET_DURATION_SECONDS_OVERSHOOT_AMOUNTS:
        if target_duration >= target_duration_seconds:
            return target_duration + overshoot_amount
    return target_duration


def calculate_video_queue_score(
    video: Video,
    queue_params: QueueParams,
) -> float:
    scoring_data = queue_params[video.user_id]
    priority_score = scoring_data.priority_score
    substring_priority_scores = scoring_data.substring_priority_scores

    for substring, score in substring_priority_scores.items():
        if (
            substring.lower() in video.title.lower()
            or substring.lower() in video.description.lower()
        ):
            if score > priority_score:
                priority_score = score

    DURATION_SECONDS_SCORE_MULTIPLIERS.sort(key=lambda x: x[0], reverse=True)
    for seconds, multiplier in DURATION_SECONDS_SCORE_MULTIPLIERS:
        if video.length_seconds >= seconds:
            priority_score *= multiplier
            break

    DAYS_SINCE_UPLOAD_SCORE_MULTIPLIERS.sort(key=lambda x: x[0], reverse=True)
    for days, multiplier in DAYS_SINCE_UPLOAD_SCORE_MULTIPLIERS:
        if video.days_since_upload >= days:
            priority_score *= multiplier
            break

    return float(priority_score)


def calculate_queue(
    videos: List[Video],
    target_duration_minutes: int,
    queue_params: QueueParams = QUEUE_PARAMS,
) -> List[Video]:
    """Takes a list of videos, calculates their individual queue scores, and
    accordingly orders them into a queue of approximately the given target duration.
    """

    # calculate scores
    scores: List[Tuple[Video, float]] = []
    for video in videos:
        score = calculate_video_queue_score(video, queue_params)
        scores.append((video, score))

    # sort by score, descending
    scores.sort(key=lambda x: x[1], reverse=True)

    # generate queue
    queue: List[Video] = []
    target_seconds = target_duration_minutes * 60
    max_seconds = calculate_max_duration_from_target_duration_seconds(
        target_seconds
    )
    queued_watchime_seconds = 0
    for video, score in scores:
        if queued_watchime_seconds + video.length_seconds > max_seconds:
            continue
        queue.append(video)
        queued_watchime_seconds += video.length_seconds
        if len(queue) >= N_QUEUE_VIDEOS_SAFETY_LIMIT:
            break

    return queue
