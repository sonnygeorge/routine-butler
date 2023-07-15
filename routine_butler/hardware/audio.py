import array
import os
import platform
import subprocess
import wave

from loguru import logger

from routine_butler.utils.logging import HARDWARE_LOG_LVL


def create_new_wav_given_volume_multiplier(
    input_file: str, output_file: str, volume_multiplier: float
) -> None:
    with wave.open(input_file, "rb") as wav_in:
        params = wav_in.getparams()
        audio_data = array.array("h", wav_in.readframes(wav_in.getnframes()))

    # Apply the volume multiplier to each audio sample
    adjusted_data = array.array(
        "h", (int(sample * volume_multiplier) for sample in audio_data)
    )

    with wave.open(output_file, "wb") as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(adjusted_data.tobytes())


def play_wav(file_path: str) -> None:
    logger.log(HARDWARE_LOG_LVL, f"Playing wav: {file_path.split('/')[-1]}")
    system = platform.system()
    if system == "Windows":
        command = [
            "powershell",
            f"(New-Object Media.SoundPlayer '{file_path}').PlaySync()",
        ]
    elif system == "Darwin":
        command = ["afplay", file_path]
    elif system == "Linux":
        command = ["aplay", file_path]
    else:
        raise NotImplementedError(f"Unsupported os: {system}")
    subprocess.run(command)


def play_wav_with_volume_adjustment(
    file_path: str, volume: float = 1.0
) -> None:
    if volume < 0.0 or volume > 1.0:
        raise ValueError("Volume must be between 0.0 and 1.0")
    if volume != 1.0:
        temp_path = os.path.splitext(file_path)[0] + "-volume-adjusted.wav"
        create_new_wav_given_volume_multiplier(file_path, temp_path, volume)
        play_wav(temp_path)
        os.remove(temp_path)
    else:
        play_wav(file_path)
