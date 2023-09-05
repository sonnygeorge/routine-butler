from typing import Optional

from nicegui import ui

# A note regarding embedding Youtube Videos:

# “Video unavailable-watch on youtube” is a common occurance which stems from any of the
# following:

#   1. The creator restricted embedding in the Video Privacy settings
#   2. The video is age-restricted (you must be logged in to view such videos)
#   3. The video was given a copyright strike

# Users should remove channels where this occurs often from their queue parameters in
# order to have a better experience.

HEIGHT = 315
WIDTH = 560


def youtube_embed(
    video_id: str, autoplay: bool = True, start_seconds: Optional[int] = None
) -> ui.element:
    """Plays a youtube video at 2x speed."""

    # Add player with using iframe html
    html = f'<iframe width="{WIDTH}" height="{HEIGHT}" '
    html += f'src="http://www.youtube.com/embed/{video_id}'
    if autoplay is True:
        html += "?autoplay=1"
    if start_seconds is not None:
        html += f"&start={start_seconds}"
    html += '" frameborder="0" allow="autoplay"></iframe>'
    return ui.html(html)
