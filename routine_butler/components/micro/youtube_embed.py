from nicegui import ui


class YoutubeEmbed(ui.element):
    def __init__(self, video_id: str) -> None:
        super().__init__("iframe")
        self.default_style()
        self.set_video_id(video_id)

    def set_video_id(self, video_id: str) -> None:
        self.props(f"src=https://www.youtube-nocookie.com/embed/{video_id}")

    def default_style(self) -> None:
        self.props("width=560")
        self.props("height=315")
        self.props("frameborder=0")
        self.props(
            "allow=accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        )
        self.props("allowfullscreen")
