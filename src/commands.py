import audioop
import os
import simpleaudio as sa
import wave


def playAudio(filename, reverse=False, volume=None, speed=None):
    with wave.open(filename, "rb") as wave_read:
        audio_data = wave_read.readframes(wave_read.getnframes())
        num_channels = wave_read.getnchannels()
        bytes_per_sample = wave_read.getsampwidth()
        sample_rate = wave_read.getframerate()

    if reverse:
        audio_data = audioop.reverse(audio_data, bytes_per_sample)
    if volume is not None and volume >= 0:
        audio_data = audioop.mul(audio_data, bytes_per_sample, volume)
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
