from typing import Optional

from nicegui import ui
from pydantic import BaseModel

from routine_butler.components import micro


class YoutubeGui:
    def __init__(self, data: "Youtube", on_complete: callable):
        self.data = data
        self.on_complete = on_complete

        with micro.card():
            ui.label("Player that shows a queue of Youtube vids in succession")
            skip_button = ui.button("Next Video")

        skip_button.on("click", self.handle_video_complete)
        # player.on("video_complete", self.handle_video_complete)

    def get_queue(self):
        """Given the most recently published videos from the channels to which data.user
        is subscribed, prepares a queue of youtube videos who summed watchtime aims to be
        close to data.watchtime_minutes"""
        pass

    def handle_video_complete(self):  # pseudocode
        if "queue is empty":
            self.on_complete()
        else:
            "switch to next video"
            "queue.pop"


class Youtube(BaseModel):
    # Youtube user whose subsriptions will be the source for generating the queue
    username: Optional[str] = None
    # Password (if needed)...
    # If so, it would be good to for the components.program_configurer.plugin_grid
    # input element to hide the password with ******** characters...
    password: Optional[str] = None
    # The total watchtime that the widget will aim for when generating the queue
    watchtime_minutes: int = 25
    # ...

    def administer(self, on_complete: callable):
        YoutubeGui(self, on_complete=on_complete)
