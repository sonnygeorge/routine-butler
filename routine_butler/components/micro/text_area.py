import subprocess

from nicegui import ui

# Don't forget to change the default keyboard to keyboard-lq1.xml
# stackoverflow.com/questions/70574505/how-to-change-the-default-matchbox-keyboard-layout


def open_keyboard():
    try:
        subprocess.Popen(["matchbox-keyboard"])
    except FileNotFoundError:
        pass


def close_keyboard():
    try:
        subprocess.run(["killall", "matchbox-keyboard"])
    except FileNotFoundError:
        pass


def text_area(*args, **kwargs) -> ui.textarea:
    input = ui.textarea(*args, **kwargs)
    input.on("focus", open_keyboard)
    input.on("blur", close_keyboard)
    return input
