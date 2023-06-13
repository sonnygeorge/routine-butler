import urllib.request as request
import re


REG_VIDEO_ID = '"videoId":"([\w\d]*)"'


def __extract_videos_id(page: str) -> list:
    result = []
    for video_id in re.findall(REG_VIDEO_ID, page):
        if video_id not in result:
            result.append(video_id)

    return result


def subscriptions_feed(cookie: str) -> list[str]:
    req = request.Request(
        "https://www.youtube.com/feed/subscriptions",
    )
    req.add_header("cookie", cookie)
    page = request.urlopen(req).read()
    return __extract_videos_id(str(page))
