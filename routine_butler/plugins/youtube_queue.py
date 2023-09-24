import asyncio

from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.plugins._youtube_queue.calculate_queue import (
    calculate_queue,
)
from routine_butler.plugins._youtube_queue.retrieve_video_data import (
    retrieve_video_data,
)
from routine_butler.plugins._youtube_queue.utils import (
    add_to_watched_video_history,
    get_watched_video_history,
)

# FIXME: add listener to video finish to prevent navigation to suggested videos


class YoutubeQueueGui:
    def __init__(self, data: "YoutubeQueue", on_complete: callable):
        self.data = data
        self.on_complete = on_complete
        self.cur_video_idx = 0

        self.card = micro.card().classes("flex flex-col items-center")
        with self.card:
            self.progress = ui.label("Loading...")

        ui.timer(0.1, self.generate_queue, once=True)

    def add_player_to_ui(self):
        with self.card:
            self.video_player_frame = ui.element("div")
            ui.separator().classes("my-1")
            with ui.row().classes("w-5/6 flex items-center justify-between"):
                left_btn = ui.button("<", on_click=self.hdl_previous_video)
                left_btn.classes("w-36")
                with ui.column().classes("items-center"):
                    self.idx_label = ui.label("").style("font-size: 1.25rem")
                    self.id_label = ui.label("").classes("text-xs")
                right_btn = ui.button(">", on_click=self.hdl_next_video)
                right_btn.classes("w-36")

    def _update_ui(self):
        if len(self.video_uids) == 0:
            return
        cur_id = self.video_uids[self.cur_video_idx]
        self.id_label.set_text(cur_id)
        self.video_player_frame.clear()
        with self.video_player_frame:
            self.video_player = micro.youtube_embed(cur_id)
        label_text = f"Video {self.cur_video_idx + 1}/{len(self.video_uids)}"
        self.idx_label.set_text(label_text)

    async def generate_queue(self) -> list[str]:
        # Scrape video datas
        videos = await retrieve_video_data(self.progress)
        # Expunge already watched videos from raw data
        watched = get_watched_video_history()
        videos = [v for v in videos if v.uid not in watched]
        # Generate queue with algorithm
        queue = calculate_queue(videos, self.data.target_duration_minutes)
        self.video_uids = [video.uid for video in queue]
        # Save queue ids and add them to watch history
        # TODO: change to when actually watched (not when queue generated)?
        add_to_watched_video_history(self.video_uids)
        # Update ui
        self.card.clear()
        self.add_player_to_ui()
        self._update_ui()
        # Handle the case of no videos found
        if len(self.video_uids) == 0:
            await asyncio.sleep(1.5)
            ui.notify("No videos found", type="negative")
            await asyncio.sleep(2.5)
            self.on_complete()

    def hdl_next_video(self):
        if self.cur_video_idx + 1 == len(self.video_uids):  # No more videos
            self.on_complete()
        else:
            self.cur_video_idx += 1
            self._update_ui()

    def hdl_previous_video(self):
        self.cur_video_idx = (self.cur_video_idx - 1) % len(self.video_uids)
        self._update_ui()


class YoutubeQueue(BaseModel):
    target_duration_minutes: int = 25

    def administer(self, on_complete: callable):
        YoutubeQueueGui(self, on_complete=on_complete)
