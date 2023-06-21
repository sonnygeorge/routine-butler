from nicegui import ui

# A note regarding embedding Youtube Videos:

# “Video unavailable-watch on youtube” is a common occurance which stems from any of the
# following:

#   1. The creator restricted embedding in the Video Privacy settings
#   2. The video is age-restricted (you must be logged in to view such videos)
#   3. The video was given a copyright strike

# Users should remove channels where this occurs often from their queue parameters in
# order to have a better experience.


class YoutubeEmbed(ui.element):
    def __init__(self, video_id: str) -> None:
        super().__init__("iframe")
        self.default_style()
        self.set_video_id(video_id)

    def set_video_id(self, video_id: str) -> None:
        self.props(f"src=https://www.youtube-nocookie.com/embed/{video_id}")

    def default_style(self) -> None:
        self.props("width=560 height=315 frameborder=0 allowfullscreen")
        self.props(
            "allow=accelerometer; autoplay; clipboard-write; encrypted-media; "
            "gyroscope; picture-in-picture; web-share"
        )


def youtube_embed(video_id: str) -> YoutubeEmbed:
    return YoutubeEmbed(video_id=video_id)
