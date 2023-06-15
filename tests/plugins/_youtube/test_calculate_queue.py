from routine_butler.plugins._youtube.calculate_queue import (
    ALLOWED_TARGET_DURATION_SECONDS_OVERSHOOT_AMOUNTS,
    DAYS_SINCE_UPLOAD_SCORE_MULTIPLIERS,
    DURATION_SECONDS_SCORE_MULTIPLIERS,
    calculate_max_duration_from_target_duration_seconds,
    calculate_queue,
    calculate_video_queue_score,
)
from routine_butler.plugins._youtube.utils import ChannelScoringData, Video

TEST_VIDEO_ID = "test_video_id"
TEST_USER_ID = "test_user_id"
TEST_VIDEO_TITLE = "test_video_title"
TEST_VIDEO_DESCRIPTION = "test_video_description"
TEST_VIDEO_LENGTH_SECONDS = 60
TEST_VIDEO_DAYS_SINCE_UPLOAD = 0

TEST_VIDEO = Video(
    uid=TEST_VIDEO_ID,
    user_id=TEST_USER_ID,
    title=TEST_VIDEO_TITLE,
    description=TEST_VIDEO_DESCRIPTION,
    length_seconds=TEST_VIDEO_LENGTH_SECONDS,
    days_since_upload=TEST_VIDEO_DAYS_SINCE_UPLOAD,
)

TEST_SUBSTRING = "test"
SUBSTRING_PRIORITY_SCORE = 50
CHANNEL_PRIORITY_SCORE = 100
TEST_SUBSTRING_PRIORITY_SCORES = {TEST_SUBSTRING: SUBSTRING_PRIORITY_SCORE}
TEST_SCORING_DATA = ChannelScoringData(
    priority_score=CHANNEL_PRIORITY_SCORE,
    substring_priority_scores=TEST_SUBSTRING_PRIORITY_SCORES,
)
TEST_QUEUE_PARAMS = {"test_user_id": TEST_SCORING_DATA}


def test_older_videos_score_worse():
    multipliers = DAYS_SINCE_UPLOAD_SCORE_MULTIPLIERS.copy()
    multipliers.sort(key=lambda x: x[0])
    ascending_days_since_uploads = [days for days, _ in multipliers]

    videos = []
    for days_since_upload in ascending_days_since_uploads:
        video = TEST_VIDEO.copy()
        video.days_since_upload = days_since_upload
        videos.append(video)

    queue_scores = [
        calculate_video_queue_score(video, TEST_QUEUE_PARAMS)
        for video in videos
    ]
    assert queue_scores == sorted(queue_scores, reverse=True)


def test_longer_videos_score_worse():
    multipliers = DURATION_SECONDS_SCORE_MULTIPLIERS.copy()
    multipliers.sort(key=lambda x: x[0])
    ascending_durations = [seconds for seconds, _ in multipliers]

    videos = []
    for duration in ascending_durations:
        video = TEST_VIDEO.copy()
        video.length_seconds = duration
        videos.append(video)

    queue_scores = [
        calculate_video_queue_score(video, TEST_QUEUE_PARAMS)
        for video in videos
    ]
    assert queue_scores == sorted(queue_scores, reverse=True)


def test_substring_priority_score_takes_precedence():
    queue_params = TEST_QUEUE_PARAMS.copy()
    queue_params[TEST_USER_ID].priority_score = 50
    queue_params[TEST_USER_ID].substring_priority_scores = {"awesome": 100}

    video = TEST_VIDEO.copy()
    video.description = "awesome description"
    video.title = "awesome title"

    queue_score_w_found_substring = calculate_video_queue_score(
        video, queue_params
    )

    queue_params[TEST_USER_ID].substring_priority_scores = {
        "something not in the title or description": 100
    }

    queue_score_w_not_found_substring = calculate_video_queue_score(
        video, queue_params
    )

    assert queue_score_w_found_substring > queue_score_w_not_found_substring


def test_calculate_max_duration_from_target_duration_seconds():
    overshoots = ALLOWED_TARGET_DURATION_SECONDS_OVERSHOOT_AMOUNTS.copy()
    overshoots.sort(key=lambda x: x[0])
    correct_max_durations = [
        duration + overshoot for duration, overshoot in overshoots
    ]
    calculated_max_durations = [
        calculate_max_duration_from_target_duration_seconds(duration)
        for duration, _ in overshoots
    ]
    assert calculated_max_durations == correct_max_durations


def test_calculate_queue():
    multipliers = DAYS_SINCE_UPLOAD_SCORE_MULTIPLIERS.copy()
    multipliers.sort(key=lambda x: x[0])
    ascending_days_since_uploads = [days for days, _ in multipliers]

    video = TEST_VIDEO.copy()
    videos_sorted_newest_to_oldest = []
    for days_since_upload in ascending_days_since_uploads:
        video.days_since_upload = days_since_upload
        videos_sorted_newest_to_oldest.append(video.copy())

    for target_duration_minutes in range(
        1, len(videos_sorted_newest_to_oldest) + 1
    ):
        max_duration = calculate_max_duration_from_target_duration_seconds(
            target_duration_minutes * 60
        )

        n_videos_the_queue_can_hold = max_duration / TEST_VIDEO_LENGTH_SECONDS
        n_videos_the_queue_can_hold = int(n_videos_the_queue_can_hold)

        expected_queue = videos_sorted_newest_to_oldest[
            :n_videos_the_queue_can_hold
        ]  # since the newer videos will have the higher queue scores

        calculated_queue = calculate_queue(
            queue_params=TEST_QUEUE_PARAMS,
            videos=videos_sorted_newest_to_oldest,
            target_duration_minutes=target_duration_minutes,
        )

        assert calculated_queue == expected_queue
