import time

import remi

from utils import LOGO_TEXT_ART, get_clock_text_art

LOGO_TEXT_ART = LOGO_TEXT_ART.replace(" ", " ")
COLOR = "#007399"
CLOCK_FONT_SIZE = "5px"
LOGO_FONT_SIZE = "10px"
DATE_FONT_SIZE = "14px"
MOYAI_FONT_SIZE = "38px"
MOYAI_SHADOW = "0px 0px 3px rgb(0, 0, 0, .2)"
SIDE_PADDING = "20px"


def fill_vbox_with_multiline_text(
    vbox: remi.gui.VBox, text: str, text_align: str = "right"
):
    """Takes a VBox, clears it, and fills it with a multiline text"""
    if len(vbox.children) != 0:
        children = list(vbox.children.values())
        for child in children:
            vbox.remove_child(child)
    for line in text.split("\n"):
        if line.strip() or " " in line:
            row = remi.gui.Label(
                line,
                style={
                    "width": "100%",
                    "margin": "0px 0px",
                    "text-align": text_align,
                },
            )
            vbox.append(row)


class Header(remi.gui.HBox):
    def __init__(self):
        remi.gui.Widget.__init__(
            self, style={"box-shadow": "0px 0px 10px rgba(0, 0, 0, 0.5)"}
        )
        self.css_width = "100%"
        self.css_height = "70px"
        self.css_direction = "row"
        self.css_background_color = COLOR
        self.css_color = "white"
        self.css_font_family = "Courier"

        # moyai
        self.moyai_box = remi.gui.VBox(style={"padding-left": SIDE_PADDING})
        self.moyai_box.css_width = "30px"
        self.moyai_box.css_height = "100%"
        self.moyai_box.css_font_size = MOYAI_FONT_SIZE
        self.moyai_box.css_align_self = "flex-start"
        self.moyai_box.css_float = "left"
        self.moyai_box.css_background_color = COLOR
        self.moyai = remi.gui.Label("🗿", style={"text-shadow": MOYAI_SHADOW})
        self.moyai.css_align_self = "flex-start"
        self.moyai.css_background_color = COLOR
        self.moyai_box.append(self.moyai)
        self.append(self.moyai_box, "moyai")

        # logo text
        self.logo_box = remi.gui.VBox(style={"padding-left": SIDE_PADDING})
        self.logo_box.css_width = "160px"
        self.logo_box.css_height = "100%"
        self.logo_box.css_font_size = LOGO_FONT_SIZE
        self.logo_box.css_align_self = "flex-start"
        self.logo_box.css_float = "left"
        self.logo_box.css_background_color = COLOR
        self.logo = remi.gui.VBox()
        self.logo.css_align_self = "flex-start"
        self.logo.css_background_color = COLOR
        fill_vbox_with_multiline_text(self.logo, LOGO_TEXT_ART)
        self.logo.css_font_weight = "bold"
        self.logo_box.append(self.logo)
        self.append(self.logo_box, "logo")

        # clock
        self.clock_box = remi.gui.VBox(style={"padding-right": SIDE_PADDING})
        self.clock_box.css_width = "160px"
        self.clock_box.css_height = "100%"
        self.clock_box.css_font_size = CLOCK_FONT_SIZE
        self.clock_box.css_align_self = "flex-end"
        self.clock_box.css_float = "right"
        self.clock_box.css_background_color = COLOR
        self.clock = remi.gui.VBox()
        self.clock.css_align_self = "flex-end"
        self.clock.css_background_color = COLOR
        fill_vbox_with_multiline_text(
            self.clock, get_clock_text_art("00:00:00")
        )
        self.clock_box.append(self.clock)
        self.append(self.clock_box, "clock")

        # date
        self.date_box = remi.gui.VBox(style={"padding-right": SIDE_PADDING})
        self.date_box.css_width = "60px"
        self.date_box.css_height = "100%"
        self.date_box.css_font_size = DATE_FONT_SIZE
        self.date_box.css_align_self = "flex-end"
        self.date_box.css_float = "right"
        self.date_box.css_background_color = COLOR
        self.date = remi.gui.VBox()
        self.date.css_align_self = "flex-end"
        self.date.css_background_color = COLOR
        fill_vbox_with_multiline_text(self.date, "Mon\nJan 01")
        self.date_box.append(self.date)
        self.append(self.date_box, "date")

        self.update_datetime()

    def update_datetime(self):
        """Updates the text in header's date and clock display"""
        t = time.localtime()
        t_str = time.asctime(t)
        fill_vbox_with_multiline_text(
            self.clock, get_clock_text_art(t_str.split(" ")[3])
        )
        fill_vbox_with_multiline_text(
            self.date,
            f"{t_str.split(' ')[0]}\n{t_str.split(' ')[1]} {t_str.split(' ')[2]}",
        )

    def idle(self):
        """Gets called every update_interval seconds"""
        self.update_datetime()
