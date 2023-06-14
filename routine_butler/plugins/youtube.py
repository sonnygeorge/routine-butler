from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro
from routine_butler.plugins._youtube.get_video_data import subscriptions_feed


class YoutubeGui:
    def __init__(self, data: "Youtube", on_complete: callable):
        self.data = data
        self.on_complete = on_complete

        self.videos = self.get_queue()
        self.current_video_index = 0

        with micro.card():
            self.video_index = ui.label("")
            self.video_player = micro.YoutubeEmbed("")

            with ui.row() as root:
                root.classes("w-full flex items-center justify-around")

                ui.button("<", on_click=self.handle_previous_video)
                ui.label(f"Videos: {len(self.videos)}")
                ui.button(">", on_click=self.handle_next_video)

        self.__update()

    def get_queue(self) -> list[str]:
        return subscriptions_feed(self.data.cookie)

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
    cookie: str = ""
    watchtime_minutes: int = 25

    def administer(self, on_complete: callable):
        YoutubeGui(self, on_complete=on_complete)
