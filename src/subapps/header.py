import time

import remi

from subapps.subapp import SubApp
from utils import add_default_styles, get_fancy_clock_string
from states import states


LOGO_TEXT = """
╔════════════════════════════════════════════════════╗
║░█████╗░░█████╗░░██████╗░██████╗██╗██╗░░░██╗░██████╗║
║██╔══██╗██╔══██╗██╔════╝██╔════╝██║██║░░░██║██╔════╝║
║██║░░╚═╝███████║╚█████╗░╚█████╗░██║██║░░░██║╚█████╗░║
║██║░░██╗██╔══██║░╚═══██╗░╚═══██╗██║██║░░░██║░╚═══██╗║
║╚█████╔╝██║░░██║██████╔╝██████╔╝██║╚██████╔╝██████╔╝║
║░╚════╝░╚═╝░░╚═╝╚═════╝░╚═════╝░╚═╝░╚═════╝░╚═════╝░║
╚════════════════════════════════════════════════════╝ 
"""

# LOGO_TEXT = """
# ╔═════════════════════════════════════════════════════════════╗
# ║ .▄████▄. .▄▄▄ . . . .██████ . ██████ .██░ █▓. .██ . ██████. ║  
# ║ ▒██▀ ▀█. ▒████▄ . .▒██ . .▒ ▒██. .▒▒ ░██░ ██. ░██░ ██▒ . ▒. ║ 
# ║ ▒▓█. . ▄ ▒██. ▀█▄ .░ ▓██▄ . ░ ▓██▄ . ▒██░.██. ▒██░. ▓██▄. . ║ 
# ║ ▒▓▓▄ ▄██▒░██▄▄▄▄██ . ▒ .░██▒. ▒ .░██▒░██░░▓█. ░██░. ▒ .░██▒ ║
# ║ ▒ ▓███▀ ░ ▓█ . ▓██▒▒██████▒░.██████▒▒░██░░▒█████▓ ▒██████▒▒ ║
# ║ ░ ░▒ ▒ .░ ▒▒ . ▓▒█░▒ ▒▓▒ ▒░░▒ ▒▓▒ ▒ ░░▓. ░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░ ║
# ║ . .░ ▒ .▒ . ▒▒ ░░ ░▒. ░. ▒░░▒ .░.░ ▒.░░░▒░ ░ ░ ░ ░▒ ░░ ░░ . ║
# ║ ░. . . . . ░ . ▒. .░ .░. ░░ ░ .░. ░ . ▒ ░ ░░░ ░ ░ ░ ░░ .░ . ║ 
# ║ ▒ ░. . .░. . . ░. ░. . . ░. . . . ░ . ░ . . ░ . . . ░. .░ . ║
# ╚═════════════════════════════════════════════════════════════╝ 
# """

LOGO_TEXT = r'''
 ██████  █████  ███████ ███████ ██ ██    ██ ███████ 
██      ██   ██ ██      ██      ██ ██    ██ ██      
██      ███████ ███████ ███████ ██ ██    ██ ███████ 
██      ██   ██      ██      ██ ██ ██    ██      ██ 
 ██████ ██   ██ ███████ ███████ ██  ██████  ███████ 
'''

LOGO_TEXT = LOGO_TEXT.replace("░", " ")

LOGO_TEXT = LOGO_TEXT.replace(" ", " ").replace("C", "█").replace("s", "█").replace("i", "█").replace("u", "█")

COLOR = "#333366"
CLOCK_FONT_SIZE = "5px"
LOGO_FONT_SIZE = "6px"
SIDE_PADDING = "20px"


def fill_vbox_with_multiline_text(vbox: remi.gui.VBox, text: str):
    if len(vbox.children) != 0:
        children = list(vbox.children.values())
        for child in children:
            vbox.remove_child(child)
    for line in text.split("\n"):
        if line.strip():
            row = remi.gui.Label(
                line, style={"width": "100%", "margin": "0px 0px"}
            )
            vbox.append(row)


class HeaderContainer(remi.gui.HBox):
    def __init__(self):
        remi.gui.Widget.__init__(self)
        add_default_styles(self)
        self.css_width = "100%"
        self.css_height = "70px"
        self.css_direction = "row"
        self.css_background_color = COLOR
        self.css_font_family = "Monospace"
        self.css_color = "white"

        # logo text
        self.logo_box = remi.gui.VBox(style={"padding-left": SIDE_PADDING})
        self.logo_box.css_width = "37%"
        self.logo_box.css_height = "100%"
        self.logo_box.css_font_size = LOGO_FONT_SIZE
        self.logo_box.css_align_self = "flex-start"
        self.logo_box.css_float = "left"
        self.logo_box.css_background_color = COLOR
        self.logo = remi.gui.VBox()
        self.logo.css_align_self = "flex-start"
        self.logo.css_background_color = COLOR
        fill_vbox_with_multiline_text(self.logo, LOGO_TEXT)
        self.logo_box.append(self.logo)
        self.append(self.logo_box, "logo")

        # clock
        self.clock_box = remi.gui.VBox(style={"padding-right": SIDE_PADDING})
        self.clock_box.css_width = "45%"
        self.clock_box.css_height = "100%"
        self.clock_box.css_font_size = CLOCK_FONT_SIZE
        self.clock_box.css_align_self = "flex-end"
        self.clock_box.css_float = "right"
        self.clock_box.css_background_color = COLOR
        self.clock = remi.gui.VBox()
        self.clock.css_align_self = "flex-end"
        self.clock.css_background_color = COLOR
        fill_vbox_with_multiline_text(self.clock, get_fancy_clock_string("00:00:00"))
        self.clock_box.append(self.clock)
        self.append(self.clock_box, "clock")

        self.update_time()

    def on_button_clicked(self, _):
        button_was_already_clicked = states.header_button_was_clicked
        if button_was_already_clicked:
            # We "unclickify" the button
            states.header_button_was_clicked = False
            self.button.text = "not clicked"
        else:
            # We "clickify" the button
            states.header_button_was_clicked = True
            self.button.text = "clicked"

    def update_time(self):
        t = time.localtime()
        t_str = time.asctime(t)
        fill_vbox_with_multiline_text(self.clock, get_fancy_clock_string(t_str.split(" ")[3]))


class Header(SubApp):
    def __init__(self, name: str):
        self.name = name
        self.container = HeaderContainer()

    def should_be_on_stage(self):
        # We want the header to always be "on stage"
        return True

    def do_stuff(self):
        self.container.update_time()
