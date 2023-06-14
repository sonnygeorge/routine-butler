from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.plugins._youtube.calculate_queue import calculate_queue
from routine_butler.plugins._youtube.retrieve_video_data import (
    retrieve_video_data,
)


class YoutubeGui:
    def __init__(self, data: "Youtube", on_complete: callable):
        self.data = data
        self.on_complete = on_complete  # FIXME: This is never called
        self.current_video_index = 0

        self.card = micro.card()

        with self.card:
            self.progress_label = ui.label("Loading...")

        ui.timer(0.1, self.generate_queue, once=True)

    def add_player_to_ui(self):
        with self.card:
            self.video_index = ui.label("")
            self.video_player = micro.YoutubeEmbed("")

            with ui.row() as root:
                root.classes("w-full flex items-center justify-around")

                ui.button("<", on_click=self.handle_previous_video)
                ui.label(f"Videos: {len(self.videos)}")
                ui.button(">", on_click=self.handle_next_video)

    def generate_queue(self) -> list[str]:
        videos = retrieve_video_data(self.progress_label)
        queue = calculate_queue(videos, self.data.target_duration_minutes)
        self.videos = [video.id for video in queue]
        self.card.clear()
        self.add_player_to_ui()
        self.__update()

    def __update(self):
        self.video_player.set_video_id(self.videos[self.current_video_index])
        self.video_index.set_text(
            f"Current Video: {self.current_video_index + 1}"
        )

    def handle_next_video(self):
        self.current_video_index = (self.current_video_index + 1) % len(
            self.videos
        )
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
