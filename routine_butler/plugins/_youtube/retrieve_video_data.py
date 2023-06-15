from typing import List

import chromedriver_autoinstaller
from bs4 import BeautifulSoup
from loguru import logger
from nicegui import ui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from routine_butler.plugins._youtube.schema import Video
from routine_butler.plugins._youtube.utils import QUEUE_PARAMS

chromedriver_autoinstaller.install()


VIDEO_GRID_ELMNT = "div"
VIDEO_GRID_CLASS = "style-scope ytd-rich-grid-media"

TITLE_ELMNT = "yt-formatted-string"
TITLE_ID = "video-title"

TITLE_LINK_ELMNT = "a"
TITLE_LINK_ID = "video-title-link"

RTIME_ELMNT = "span"
RTIME_CLASS = "style-scope ytd-thumbnail-overlay-time-status-renderer"

METADATA_ELMNT = "span"
METADATA_CLASS = "inline-metadata-item style-scope ytd-video-meta-block"


def get_title_from_soup(video_soup: BeautifulSoup) -> str:
    return video_soup.find(TITLE_ELMNT, id=TITLE_ID).text


def get_id_from_soup(video_soup: BeautifulSoup) -> str:
    href = video_soup.find(TITLE_LINK_ELMNT, id=TITLE_LINK_ID)["href"]
    return href.split("?v=")[1]


def get_runtime_seconds_from_soup(video_soup: BeautifulSoup) -> str:
    runtime = video_soup.find(RTIME_ELMNT, class_=RTIME_CLASS).text
    split_string = runtime.split(":")
    if len(split_string) == 2:
        minutes, seconds = split_string
        return int(minutes) * 60 + int(seconds)
    elif len(split_string) == 3:
        hours, minutes, seconds = split_string
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)


def get_days_since_upload_from_soup(video_soup: BeautifulSoup) -> str:
    metadata_items: list[BeautifulSoup]  # trivial typehint to satisfy mypy
    metadata_items = video_soup.find_all(METADATA_ELMNT, class_=METADATA_CLASS)

    if len(metadata_items) != 2:
        logger.warning(
            "Unexpected number of inline metadata items in video grid element"
        )
        return 60  # HOTFIX: default to 60 days if occurs

    # 2nd metadata item ought to be time since upload (1st = view count)
    time_string = metadata_items[1].text

    if "hour" in time_string:
        return 0
    elif "day" in time_string:
        return int(time_string.split(" ")[0])
    elif "week" in time_string:
        return int(time_string.split(" ")[0]) * 7
    elif "month" in time_string:
        return int(time_string.split(" ")[0]) * 30
    else:
        return int(time_string.split(" ")[0]) * 365


def wait_until_video_grid_is_loaded(driver: WebDriver) -> None:
    """Waits until all all runtime elements are loaded on the page, indicating that the
    video grid has been loaded fully loaded"""
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, RTIME_CLASS))
    )


def get_channel_videos(user_id: str, driver: WebDriver) -> List[Video]:
    """Given a Youtube channel ID, retrieves data from channel's videos page to populate
    a list of Video objects."""
    url = f"https://www.youtube.com/{user_id}/videos"
    driver.get(url)
    wait_until_video_grid_is_loaded(driver)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    video_grid_individual_soups = soup.find_all(
        VIDEO_GRID_ELMNT, class_=VIDEO_GRID_CLASS
    )
    videos = []
    for video_element in video_grid_individual_soups:
        html = str(video_element)
        if (
            TITLE_LINK_ID not in html
            or RTIME_CLASS not in html
            or METADATA_CLASS not in html
        ):
            continue
        video = Video(
            uid=get_id_from_soup(video_element),
            user_id=user_id,
            title=get_title_from_soup(video_element),
            description="",
            length_seconds=get_runtime_seconds_from_soup(video_element),
            days_since_upload=get_days_since_upload_from_soup(video_element),
        )
        videos.append(video)
    return videos


def retrieve_video_data(progress_label: ui.label) -> list[Video]:
    """Using the Youtube channel IDs in QUEUE_PARAMS, retrieves data from each channel's
    videos page (usually shows up to 30 most recent videos) and returns a list of Video
    objects with the retrieved data."""

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    user_ids = QUEUE_PARAMS.keys()
    video_lists = []
    for user_id in user_ids:
        video_lists.append(get_channel_videos(user_id, driver))
        msg = f"Scraped {len(video_lists)}/{len(user_ids)} YouTube channels"
        progress_label.set_text(msg)  # FIXME: UI not updating
        logger.info(msg)

    return sum(video_lists, [])  # (flattens list of lists to a single list)
