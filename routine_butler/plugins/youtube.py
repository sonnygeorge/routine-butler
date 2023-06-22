from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.plugins._youtube.calculate_queue import calculate_queue
from routine_butler.plugins._youtube.retrieve_video_data import (
    retrieve_video_data,
)
from routine_butler.plugins._youtube.utils import (
    add_to_watched_video_history,
    get_watched_video_history,
)

# FIXME: add listener to video finish to prevent navigation to suggested videos


class YoutubeGui:
    def __init__(self, data: "Youtube", on_complete: callable):
        self.data = data
        self.on_complete = on_complete
        self.cur_video_idx = 0

        self.card = micro.card().classes("flex flex-col items-center")
        with self.card:
            self.progress = ui.label("Loading...")

        ui.timer(0.1, self.generate_queue, once=True)

    def add_player_to_ui(self):
        with self.card:
            self.video_player = micro.youtube_embed("")
            ui.separator().classes("my-2")
            with ui.row().classes("w-5/6 flex items-center justify-between"):
                left_btn = ui.button("<", on_click=self.hdl_previous_video)
                left_btn.classes("w-36")
                self.idx_label = ui.label("").classes("text-lg text-gray-900")
                right_btn = ui.button(">", on_click=self.hdl_next_video)
                right_btn.classes("w-36")

    def _update_ui(self):
        self.video_player.set_video_id(self.videos[self.cur_video_idx])
        label_text = f"Video {self.cur_video_idx + 1}/{len(self.videos)}"
        self.idx_label.set_text(label_text)

    async def generate_queue(self) -> list[str]:
        # scrape video data
        videos = await retrieve_video_data(self.progress)
        # expunge watched
        watched = get_watched_video_history()
        videos = [v for v in videos if v.uid not in watched]
        # generate queue
        queue = calculate_queue(videos, self.data.target_duration_minutes)
        # save queue ids and add them to watch history
        self.videos = [video.uid for video in queue]
        add_to_watched_video_history(self.videos)
        # update ui
        self.card.clear()
        self.add_player_to_ui()
        self._update_ui()

    def hdl_next_video(self):
        if self.cur_video_idx + 1 == len(self.videos):  # no more videos
            self.on_complete()
        else:
            self.cur_video_idx += 1
            self._update_ui()

    def hdl_previous_video(self):
        self.cur_video_idx = (self.cur_video_idx - 1) % len(self.videos)
        self._update_ui()


class Youtube(BaseModel):
    target_duration_minutes: int = 25

    def administer(self, on_complete: callable):
        YoutubeGui(self, on_complete=on_complete)
