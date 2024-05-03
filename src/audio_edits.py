"""This modules handles applying audio effects to a sound. It uses a pipeline
where each function reads a wav file, applies its edits, and then returns a WavData object.
So, note that every edit function will take a WavData object and a PlaybackOptions object,
apply an audio effect, and then return a new WavData object.
"""

import audioop
import librosa
from pydub import AudioSegment
from pydub.effects import speedup
import soundfile
import tempfile
import wave
from pathlib import Path


class WavData:
    def __init__(self, frames, params):
        self.frames = frames
        self.params = params


def _getData(file_path):
    """Create WavData object from file path to wav file."""
    with wave.open(file_path, "rb") as wr:
        return WavData(wr.readframes(wr.getnframes()), wr.getparams())


def edit(file_paths, options):
    """Applies audio effects to wav file at each file path and then concatenates
    or overlays edited sounds.
    Args:
        file_path: String List file path to wav file.
        options: PlaybackOptions object.
    """
    sounds = [_editSound(file_path, options) for file_path in file_paths]
    if options.parallel:
        return _overlay(sounds)
    return _concatenate(sounds)


def _editSound(file_path, options):
    """Applies audio effects to wav file at file_path.

    Args:
        file_path: String file path to wav file.
        options: PlaybackOptions object.
    """
    data = _getData(file_path)
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
    if speed is None:
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
    return _audioSegmentToWavData(audio)


def _volume(data, options):
    volume = options.volume
    if volume is None:
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
    with tempfile.TemporaryDirectory() as temp_dir:
        path = str(Path(temp_dir, "sound.wav"))
        with wave.open(path, mode="wb") as wav_file:
            wav_file.setparams(data.params)
            wav_file.writeframes(data.frames)
        y, sr = librosa.load(path)
        new_y = librosa.effects.pitch_shift(y, sr=sr, n_steps=options.transpose)
        soundfile.write(path, new_y, sr)
        return _getData(path)


def _cropSound(data, options):
    """Returns modified audio data for the cropped sound starting at start_percent and ending at end_percent.

    Make the buffer size a multiple of bytes-per-sample and the number of channels.
    """
    start_percent = options.start_percent
    end_percent = options.end_percent
    # Reset null positions
    if start_percent is None:
        start_percent = 0
    if end_percent is None:
        end_percent = 1

    # Calculate start and end indices
    def calculate_index(percent):
        return int(
            percent * len(data.frames) / (data.params.sampwidth * data.params.nchannels)
        ) * (data.params.sampwidth * data.params.nchannels)

    start_index = calculate_index(start_percent)
    stop_index = calculate_index(end_percent)
    new_data = data.frames[start_index:stop_index]
    return WavData(new_data, data.params)


def _concatenate(sounds):
    sounds = [
        AudioSegment(
            data=sound.frames,
            sample_width=sound.params.sampwidth,
            frame_rate=sound.params.framerate,
            channels=sound.params.nchannels,
        )
        for sound in sounds
    ]
    res = sounds[0]
    for sound in sounds[1:]:
        res = res.append(sound)
    return _audioSegmentToWavData(res)


def _overlay(sounds):
    sounds = [
        AudioSegment(
            data=sound.frames,
            sample_width=sound.params.sampwidth,
            frame_rate=sound.params.framerate,
            channels=sound.params.nchannels,
        )
        for sound in sounds
    ]
    res = sounds[0]
    for sound in sounds[1:]:
        # we need to check the length because if the overlayed sound is longer
        # than the original, it is truncated
        if len(res) >= len(sound):
            res = res.overlay(sound)
        else:
            res = sound.overlay(res)

    return _audioSegmentToWavData(res)


def _calculatePercent(
    data,
    start_sec=None,
    end_sec=None,
):
    """Calculates the start and end percent of the audio data based on the start and end seconds.

    start_percent and end_percent will both be returned as floats, even if they are not None.
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


def _audioSegmentToWavData(audio):
    # if we directly export this as a wav, it's somehow corrupted when we tried to read
    # it back and play it.
    # But, if we export it as a mp3, load it, export it as a wav, and then play that,
    # everything works as intended 💯😁

    # We originally wanted to use tempfile.NamedTemporaryFile but that has issues
    # on windows. See discussion on stack overflow here:
    # https://stackoverflow.com/questions/23212435/permission-denied-to-write-to-my-temporary-file
    with tempfile.TemporaryDirectory() as temp_dir:
        mp3_path = str(Path(temp_dir, "mp3_sound.mp3"))
        wav_path = str(Path(temp_dir, "wav_sound.wav"))
        with open(mp3_path, "w+"), open(wav_path, "w+"):
            audio.export(mp3_path, format="mp3")
            audio = AudioSegment.from_mp3(mp3_path)
            audio.export(wav_path, format="wav")
            return _getData(wav_path)
