import subprocess
import time

from routine_butler.globals import ALARM_WAV_PATH
from routine_butler.hardware.audio import play_wav_with_volume_adjustment
from routine_butler.utils.misc import close_keyboard, open_keyboard


def test_audio():
    print("testing loud sound...")
    play_wav_with_volume_adjustment(ALARM_WAV_PATH, 1.0)
    print("testing quiet sound...")
    play_wav_with_volume_adjustment(ALARM_WAV_PATH, 0.5)


def test_keyboard():
    print("testing keyboard open...")
    open_keyboard()
    time.sleep(1)
    print("testing keyboard close...")
    close_keyboard()
    time.sleep(1)


if __name__ == "__main__":
    test_audio()
    test_keyboard()
