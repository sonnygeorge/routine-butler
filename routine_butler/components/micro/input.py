import subprocess

from nicegui import ui

from routine_butler.utils import close_keyboard, open_keyboard

# Don't forget to change the default keyboard to keyboard-lq1.xml
# stackoverflow.com/questions/70574505/how-to-change-the-default-matchbox-keyboard-layout


def open_keyboard():
    subprocess.Popen(["matchbox-keyboard"])


def close_keyboard():
    subprocess.run(["killall", "matchbox-keyboard"])


def input(*args, **kwargs):
    input = ui.input(*args, **kwargs)
    input.on("focus", open_keyboard)
    input.on("blur", close_keyboard)
    return input
