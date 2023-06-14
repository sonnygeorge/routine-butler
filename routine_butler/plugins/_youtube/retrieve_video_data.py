from routine_butler.plugins._youtube.utils import QUEUE_PARAMS, Video


def retrieve_users_videos_data() -> list[Video]:
    """Takes a user's ID and returns a list of their videos."""
    user_ids = QUEUE_PARAMS.keys()
    # videos = []
    for user_id in user_ids:
        # url = f"https://www.youtube.com/channel/{user_id}/videos"
        # TODO: make request(s) and extract data
        pass
