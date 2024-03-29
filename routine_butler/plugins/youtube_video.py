import asyncio
import random
import re
from enum import StrEnum
from typing import List, Optional, TypedDict

from loguru import logger
from nicegui import ui
from pydantic import BaseModel, constr

from routine_butler.components import micro
from routine_butler.globals import (
    DATAFRAME_LIKE,
    YOUTUBE_VIDEO_FOLDER_NAME,
    PlaybackRate,
)
from routine_butler.models import ProgramRun
from routine_butler.state import state
from routine_butler.utils.misc import (
    PagePath,
    PendingYoutubeVideo,
    redirect_to_page,
)

DB_QUERY_LIMIT = 120


def is_valid_youtube_id(to_check):
    if re.match(r"^[A-Za-z0-9_-]{11}$", to_check):
        return True
    else:
        return False


def is_valid_youtube_link(to_check):
    pattern = r"^https?://(?:www\.)?youtube\.com/watch\?v=[A-Za-z0-9_-]{11}$"
    if re.match(pattern, to_check):
        return True
    else:
        return False


class YoutubeVideoRunData(TypedDict):
    video_id: str
    reported_success: bool


class YoutubeVideoMode(StrEnum):
    SINGLE = "single"
    SERIES = "series"
    RANDOM = "random"


def get_last_watched_video(path_or_id: str) -> Optional[str]:
    """Returns the video ID of the most recent successfully watched YouTube video in the
    series.
    """
    # Get 1000 topmost ProgramRuns of plugin type YoutubeVideo
    filter_expr = ProgramRun.Config.orm_model.plugin_type == "YoutubeVideo"
    res: List[ProgramRun] = ProgramRun.query(
        engine=state.engine, filter_expr=filter_expr, limit=DB_QUERY_LIMIT
    )
    # Find most recent successful watch with the given path
    for run in reversed(res):
        if (
            run.plugin_dict["path_or_id"] == path_or_id
            and run.plugin_dict["mode"] == YoutubeVideoMode.SERIES
            and "reported_success" in run.run_data
            and run.run_data["reported_success"]
        ):
            return run.run_data["video_id"]
    # If no successful watch found, return None
    return None


def convert_list_from_links_to_ids_as_needed(videos: List[str]) -> List[str]:
    """Converts a list of YouTube video IDs or links to a list of YouTube video IDs.

    Also performs validation."""
    converted = []
    for vid in videos:
        if is_valid_youtube_link(vid):
            vid = vid.split("=")[1]
        if not is_valid_youtube_id(vid):
            raise ValueError(f"Invalid video ID/link: {vid}")
        converted.append(vid)
    return converted


class YoutubeVideoGui:
    def __init__(self, data: "YoutubeVideo", on_complete: callable):
        self.data = data
        self.on_complete = on_complete

        self.card = micro.card().classes("flex flex-col items-center")
        with self.card:
            self.progress = ui.label("Loading...")

        ui.timer(0.1, self.get_video_id_and_update_ui, once=True)

    async def get_video_id_and_update_ui(self):
        invalid_msg = None
        # single mode
        if self.data.mode == YoutubeVideoMode.SINGLE:
            if is_valid_youtube_id(self.data.path_or_id):
                self.video_id = self.data.path_or_id
        # series or random mode
        else:
            try:
                path = f"{YOUTUBE_VIDEO_FOLDER_NAME}/{self.data.path_or_id}"
                df_like = DATAFRAME_LIKE(path)
                videos: List[str] = sum(await df_like.get_all_data(), [])
            except Exception as e:
                invalid_msg = f"Could not load dataframe-like: {e}"
            else:
                if videos == []:
                    invalid_msg = "Dataframe-like is empty."

                try:
                    videos = convert_list_from_links_to_ids_as_needed(videos)
                except ValueError as e:
                    invalid_msg = str(e)
                else:
                    if self.data.mode == YoutubeVideoMode.SERIES:
                        last_vid = get_last_watched_video(self.data.path_or_id)
                        if last_vid is None:
                            ui.notify(
                                "No previously watched video found in recent "
                                "past for this series. Playing first video."
                            )
                            self.video_id: str = videos[0]
                        else:
                            last_vid_idx = videos.index(last_vid)
                            if last_vid_idx == len(videos) - 1:
                                ui.notify(
                                    "Last watched video is the last video in "
                                    "the series. Playing first video."
                                )
                                self.video_id: str = videos[0]
                            else:
                                self.video_id: str = videos[last_vid_idx + 1]
                    elif self.data.mode == YoutubeVideoMode.RANDOM:
                        self.video_id: str = random.choice(videos)

        if invalid_msg is None:  # if no validity issues, video is playable
            self.navigate_to_youtube_view()
        else:  # otherwise, display the error msg & complete after brief wait
            ui.notify(invalid_msg)
            logger.warning(invalid_msg)
            await asyncio.sleep(2.8)
            self.on_complete()

    def navigate_to_youtube_view(self):
        pending_video = PendingYoutubeVideo(
            video_id=self.video_id,
            start_seconds=self.data.start_seconds,
            playback_rate=self.data.playback_rate,
            autoplay=self.data.autoplay,
        )
        state.set_pending_youtube_video(pending_video)
        redirect_to_page(PagePath.YOUTUBE, n_seconds_before_redirect=0.1)


class YoutubeVideo(BaseModel):
    mode: YoutubeVideoMode = YoutubeVideoMode.SINGLE
    path_or_id: constr(min_length=1) = "QWlCcfSqfKY"
    start_seconds: int = 0
    playback_rate: PlaybackRate = PlaybackRate.PLAYBACK_RATE_NORMAL
    autoplay: bool = False

    def administer(self, on_complete: callable):
        YoutubeVideoGui(self, on_complete=on_complete)

    def estimate_duration_in_seconds(self) -> float:
        if self.mode == YoutubeVideoMode.SINGLE:
            return 6 * 60  # We have no way of guessing video length from ID
        else:  # We parse the path
            est_video_seconds = int(str(self.path_or_id).split("-")[-1])
            seconds_to_watch = est_video_seconds - self.start_seconds
            watch_time_seconds = seconds_to_watch / float(self.playback_rate)
            # add 3.5 seconds for user to click success
            total_time_seconds = watch_time_seconds + 3.5
            if not self.autoplay:
                total_time_seconds += 3  # add 3 seconds for user to click play
            return total_time_seconds
