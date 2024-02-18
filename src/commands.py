import numpy as np
import os
import simpleaudio as sa
import wave


def playAudio(filename, reverse=False, volume=None, speed=None):
    wave_read = wave.open(filename, "rb")
    audio_data = wave_read.readframes(wave_read.getnframes())
    num_channels = wave_read.getnchannels()
    bytes_per_sample = wave_read.getsampwidth()
    sample_rate = wave_read.getframerate()

    if reverse:
        raise NotImplementedError
        # wave_obj = reverseAudio(wave_obj)

    if volume is not None:
        wave_obj = changeVolume(filename, volume)

    if speed is not None and speed > 0:
        sample_rate = int(sample_rate * speed)

    wave_obj = sa.WaveObject(audio_data, num_channels, bytes_per_sample, sample_rate)
    play_obj = wave_obj.play()
    return play_obj


def playAudioWait(filename, reverse=False, volume=None, speed=None):
    playAudio(filename, reverse=reverse, volume=volume, speed=speed).wait_done()


def playSequence(filenames, reverse=False, volume=None, speed=None):
    for fname in filenames:
        playAudioWait(fname, reverse=reverse, volume=volume, speed=speed)


def playParallel(filenames, reverse=False, volume=None, speed=None):
    play_objs = []
    for fname in filenames:
        play_objs.append(playAudio(fname, reverse=reverse, volume=volume, speed=speed))
    for play_obj in play_objs:
        play_obj.wait_done()


def getSounds(dir="sounds/"):
    return os.listdir(dir)


def rename(filename, new_name):
    if len(new_name) < 4 or new_name[-4:] != ".wav":
        new_name += ".wav"
    os.rename(filename, new_name)


def changeVolume(filename, volume):
    wave_read = wave.open(filename, "rb")
    sample_width = wave_read.getsampwidth()
    sample_rate = wave_read.getframerate()

    audio_data = np.frombuffer(
        wave_read.readframes(wave_read.getnframes()), dtype=np.int16
    )
    audio_data = (audio_data * volume).astype(np.int16)
    audio_data = np.clip(audio_data, -32768, 32767)

    wave_obj = sa.WaveObject(
        audio_data.tobytes(), bytes_per_sample=sample_width, sample_rate=sample_rate
    )

    return wave_obj
