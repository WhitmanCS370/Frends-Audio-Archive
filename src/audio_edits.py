"""This modules handles applying audio effects to a sound. It uses a pipeline
where each function reads a wav file, applies its edits, and then overwrites
the wav file.
"""

import audioop
import librosa
from pydub import AudioSegment
from pydub.effects import speedup
import soundfile
import tempfile
import wave


class WavData:
    def __init__(self, frames, params):
        self.frames = frames
        self.params = params


def _get_data(file_path):
    with wave.open(file_path, "rb") as wr:
        return WavData(wr.readframes(wr.getnframes()), wr.getparams())


def edit(file_path, options):
    """Dynamically dispatches options to apply edits.

    Args:
        options: A playback_options object.
        file: A file-like object.
    """
    data = _get_data(file_path)
    if options.start_sec is not None or options.end_sec is not None:
        options.start_percent, options.end_percent = _calculatePercent(
            data,
            options.start_sec,
            options.end_sec,
        )
    # If changing how edit functions are applied, make sure that you consider the
    # effects of speeding up or reversing before cropping the sound.
    for edit in [_cropSound, _speed, _volume, _reverse, _transpose]:
        data = edit(data, options)
    return data


def _speed(data, options):
    speed = options.speed
    if speed is None or abs(1 - speed) <= 0.01 or abs(speed) <= 0.01:
        return data
    # source: https://stackoverflow.com/questions/74136596/how-do-i-change-the-speed-of-an-audio-file-in-python-like-in-audacity-without
    audio = AudioSegment(
        data=data.frames,
        sample_width=data.params.sampwidth,
        frame_rate=data.params.framerate,
        channels=data.params.nchannels,
    )
    if speed > 1:
        audio = speedup(audio, playback_speed=speed)
    else:
        altered_audio = audio._spawn(
            audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)}
        )
        audio = altered_audio.set_frame_rate(audio.frame_rate)
    # if we directly export this as a wav, it's somehow corrupted when we tried to read
    # it back and play it.
    # But, if we export it as a mp3, load it, export it as a wav, and then play that,
    # everything works as intended 💯😁
    with tempfile.TemporaryFile(suffix=".mp3") as mp3_file, tempfile.NamedTemporaryFile(
        suffix=".wav"
    ) as wav_file:
        audio.export(mp3_file, format="mp3")
        audio = AudioSegment.from_mp3(mp3_file)
        audio.export(wav_file.name, format="wav")
        return _get_data(wav_file.name)


def _volume(data, options):
    volume = options.volume
    if volume is None or volume < 0:
        return data
    new_data = audioop.mul(data.frames, data.params.sampwidth, volume)
    return WavData(new_data, data.params)


def _reverse(data, options):
    if not options.reverse:
        return data
    new_data = audioop.reverse(data.frames, data.params.sampwidth)
    return WavData(new_data, data.params)


def _transpose(data, options):
    if options.transpose is None:
        return data
    with tempfile.NamedTemporaryFile(suffix=".wav") as f:
        with wave.open(f.name, mode="wb") as wav_file:
            wav_file.setparams(data.params)
            wav_file.writeframes(data.frames)
        y, sr = librosa.load(f.name)
        new_y = librosa.effects.pitch_shift(y, sr=sr, n_steps=options.transpose)
        soundfile.write(f.name, new_y, sr)
        return _get_data(f.name)


def _cropSound(data, options):
    """Returns modified audio data for the cropped sound starting at start_percent and ending at end_percent.

    Make the buffer size a multiple of bytes-per-sample and the number of channels.

    Args:
        audio_data: bytes of audio data
        sample_rate: int sample rate of audio data
        num_channels: int number of channels in audio data.
        start_percent: The start position of the audio as a percent, ranges from 0 to 1.
        end_percent: The end position of the audio as a percent, ranges from 0 to 1.

    Raises:
        ValueError: start_percent is greater than end_percent or one of the values is
            less than 0 or greater than 1.
    """
    start_percent = options.start_percent
    end_percent = options.end_percent
    # Reset null positions
    if start_percent is None:
        start_percent = 0
    if end_percent is None:
        end_percent = 1

    # Check for invalid values
    if min(start_percent, end_percent) < 0 or max(start_percent, end_percent) > 1:
        raise ValueError("Start and end percent must be between 0 and 1")
    if start_percent >= end_percent:
        raise ValueError("Start must be less than end")

    # Calculate start and end indices
    def calculate_index(percent):
        return int(
            percent * len(data.frames) / (data.params.sampwidth * data.params.nchannels)
        ) * (data.params.sampwidth * data.params.nchannels)

    start_index = calculate_index(start_percent)
    stop_index = calculate_index(end_percent)
    new_data = data.frames[start_index:stop_index]
    return WavData(new_data, data.params)


def _calculatePercent(
    data,
    start_sec=None,
    end_sec=None,
):
    """Calculates the start and end percent of the audio data based on the start and end seconds.

    start_percent and end_percent will both be returned as floats, even if they are not None.

    Args:
        audio_data: bytes of audio data
        sample_rate: int sample rate of audio data
        num_channels: int number of channels in audio data.
        start_sec: The start position of the audio in seconds.
        end_sec: The end position of the audio in seconds.

    Raises:
        None
    """
    total_duration_seconds = len(data.frames) / (
        data.params.framerate * data.params.sampwidth * data.params.nchannels
    )

    # Calculate start percent
    if start_sec is None:
        start_percent = 0.0
    else:
        start_percent = start_sec / total_duration_seconds

    # Calculate end percent
    if end_sec is None:
        end_percent = 1.0
    else:
        end_percent = end_sec / total_duration_seconds

    return start_percent, end_percent
