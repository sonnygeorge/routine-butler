from nicegui import ui

from routine_butler.components import micro
from routine_butler.globals import PagePath
from routine_butler.plugins.youtube_video import YoutubeVideoRunData
from routine_butler.state import state
from routine_butler.utils.misc import (
    PendingYoutubeVideo,
    initialize_page,
    redirect_to_page,
)

BODY_HTML = """
    <script type="text/javascript">
    var tag = document.createElement('script');
    tag.id = 'iframe-demo';
    tag.src = 'https://www.youtube.com/iframe_api';
    var firstScriptTag = document.getElementsByTagName('script')[0];
    firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);

    var player;
    function onYouTubeIframeAPIReady() {
        player = new YT.Player('player', {
            events: {
            'onReady': onPlayerReady,
            }
        });
    }
    function onPlayerReady(event) {
        event.target.setPlaybackRate(PLAYBACK_RATE);
    }
    </script>
"""

IFRAME_HTML = """
<iframe id="player"
    width="640" height="360"
    src="{src}"
    allow="autoplay"
></iframe>
"""

IFRAME_SRC = "https://www.youtube.com/embed/{video_id}?enablejsapi=1"
IFRAME_SRC += "&start={start_seconds}"


def add_body_html(pending_youtube_video: PendingYoutubeVideo) -> None:
    html = BODY_HTML.replace(
        "PLAYBACK_RATE", str(pending_youtube_video.playback_rate)
    )
    ui.add_body_html(html)


def add_iframe(pending_youtube_video: PendingYoutubeVideo) -> ui.html:
    src = IFRAME_SRC.format(
        video_id=pending_youtube_video.video_id,
        start_seconds=pending_youtube_video.start_seconds,
    )
    if pending_youtube_video.autoplay:
        src += "&autoplay=1"
    html = IFRAME_HTML.format(
        src=src, playback_rate=pending_youtube_video.playback_rate
    )
    return ui.html(html)


@ui.page(path=PagePath.YOUTUBE)
def youtube():
    def hdl_success():
        state.set_pending_run_data_to_be_added_to_db(
            run_data=YoutubeVideoRunData(
                video_id=state.pending_youtube_video.video_id,
                reported_success=True,
            )
        )
        state.set_pending_youtube_video(None)
        redirect_to_page(PagePath.DO_ROUTINE)

    def hdl_failure():
        state.set_pending_run_data_to_be_added_to_db(
            run_data=YoutubeVideoRunData(
                video_id=state.pending_youtube_video.video_id,
                reported_success=False,
            )
        )
        state.set_pending_youtube_video(None)
        redirect_to_page(PagePath.DO_ROUTINE)

    initialize_page(page=PagePath.YOUTUBE, state=state)

    if state.pending_youtube_video is None:
        ui.label("No pending video to show...").classes("absolute-center")
        redirect_to_page(PagePath.HOME, n_seconds_before_redirect=1.7)
    else:
        add_body_html(state.pending_youtube_video)
        with micro.card().classes("flex-col items-center absolute-center"):
            add_iframe(state.pending_youtube_video)
            ui.separator()
            with ui.row():
                ui.button("Success", on_click=hdl_success)
                ui.button("Failure", on_click=hdl_failure)
