from typing import List

import chromedriver_autoinstaller
from bs4 import BeautifulSoup
from nicegui import ui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from routine_butler.plugins._youtube.utils import QUEUE_PARAMS, Video

chromedriver_autoinstaller.install()


def get_title_from_soup(soup: BeautifulSoup) -> str:
    return soup.find("yt-formatted-string", id="video-title").text


def get_id_from_soup(soup: BeautifulSoup) -> str:
    href = soup.find("a", id="video-title-link")["href"]
    return href.split("?v=")[1]


def get_runtime_seconds_from_soup(soup: BeautifulSoup) -> str:
    runtime = soup.find(
        "span", class_="style-scope ytd-thumbnail-overlay-time-status-renderer"
    ).text
    split_string = runtime.split(":")
    if len(split_string) == 2:
        minutes, seconds = split_string
        return int(minutes) * 60 + int(seconds)
    elif len(split_string) == 3:
        hours, minutes, seconds = split_string
        return int(hours) * 3600 + int(minutes) * 60 + int(seconds)


def get_days_since_upload_from_soup(soup: BeautifulSoup) -> str:
    time_string = soup.find_all(
        "span",
        class_="inline-metadata-item style-scope ytd-video-meta-block",
    )[1].text

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
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(
            (
                By.CLASS_NAME,
                "style-scope ytd-thumbnail-overlay-time-status-renderer",
            )
        )
    )


def get_channel_videos(user_id: str, driver: WebDriver) -> List[Video]:
    url = f"https://www.youtube.com/{user_id}/videos"
    driver.get(url)
    wait_until_video_grid_is_loaded(driver)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    video_grid_individual_soups = soup.find_all(
        "div", class_="style-scope ytd-rich-grid-media"
    )
    videos = []
    for video_element in video_grid_individual_soups:
        html = str(video_element)
        if (
            "video-title-link" not in html
            or "inline-metadata-item style-scope ytd-video-meta-block"
            not in html
            or "style-scope ytd-thumbnail-overlay-time-status-renderer"
            not in html
        ):
            continue
        video = Video(
            id=get_id_from_soup(video_element),
            user_id=user_id,
            title=get_title_from_soup(video_element),
            description="",
            length_seconds=get_runtime_seconds_from_soup(video_element),
            days_since_upload=get_days_since_upload_from_soup(video_element),
        )
        videos.append(video)
    return videos


def retrieve_video_data(progress_label: ui.label) -> list[Video]:
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    user_ids = QUEUE_PARAMS.keys()
    video_lists = []
    for user_id in user_ids:
        video_lists.append(get_channel_videos(user_id, driver))
        progress_msg = f"Retrieved {len(video_lists)}/{len(user_ids)} channels"
        progress_label.set_text(progress_msg)  # FIXME: UI not updating

    return sum(video_lists, [])
