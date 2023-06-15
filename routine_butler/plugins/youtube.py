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


class YoutubeGui:
    def __init__(self, data: "Youtube", on_complete: callable):
        self.data = data
        self.on_complete = on_complete
        self.current_video_index = 0

        self.card = micro.card()

        with self.card:
            self.progress_label = ui.label("Loading...")

        ui.timer(0.1, self.generate_queue, once=True)

    def add_player_to_ui(self):
        with self.card:
            self.video_player = micro.YoutubeEmbed("")
            ui.separator().classes("my-2")
            with ui.row().classes("w-full flex items-center justify-between"):
                left_btn = ui.button("<", on_click=self.handle_previous_video)
                left_btn.classes("w-1/3")
                self.video_index_label = ui.label("")
                right_btn = ui.button(">", on_click=self.handle_next_video)
                right_btn.classes("w-1/3")

    def generate_queue(self) -> list[str]:
        # scrape video data
        videos = retrieve_video_data(self.progress_label)
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
        self.__update()

    def __update(self):
        self.video_player.set_video_id(self.videos[self.current_video_index])
        self.video_index_label.set_text(
            f"Video {self.current_video_index + 1}/{len(self.videos)}"
        )

    def handle_next_video(self):
        if self.current_video_index + 1 == len(self.videos):  # no more videos
            self.on_complete()
        else:
            self.current_video_index += 1
            self.__update()

    def handle_previous_video(self):
        self.current_video_index = (self.current_video_index - 1) % len(
            self.videos
        )
        self.__update()


class Youtube(BaseModel):
    target_duration_minutes: int = 25

    def administer(self, on_complete: callable):
        YoutubeGui(self, on_complete=on_complete)
