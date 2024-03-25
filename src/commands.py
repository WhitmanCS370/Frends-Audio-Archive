import audioop
import os
from pydub import AudioSegment
from pydub.effects import speedup
import simpleaudio as sa
import tempfile
import wave

# TODO: Add docstrings

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
        audio_data, num_channels, bytes_per_sample, sample_rate = changeSpeed(
            audio_data, bytes_per_sample, sample_rate, num_channels, speed
        )
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


def changeSpeed(audio_data, bytes_per_sample, sample_rate, num_channels, speed):
    # source: https://stackoverflow.com/questions/74136596/how-do-i-change-the-speed-of-an-audio-file-in-python-like-in-audacity-without
    # NOTE: Thanks for the citation. I was unable to test this feature due to not having ffmpeg installed.
    audio = AudioSegment(
        data=audio_data,
        sample_width=bytes_per_sample,
        frame_rate=sample_rate,
        channels=num_channels,
    )
    if speed > 1:
        audio = speedup(audio, playback_speed=speed)
    else:
        altered_audio = audio._spawn(
            audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)}
        )
        audio = altered_audio.set_frame_rate(audio.frame_rate)
    # i am sorry to anybody who stumbles upon this
    # NOTE: You don't need to apologize, just explain why you did it this way.
    # if we directly export this as a wav, it's somehow corrupted when we tried to read
    # it back and play it.
    # But, if we export it as a mp3, load it, export it as a wav, and then play that,
    # everything works as intended
    with tempfile.NamedTemporaryFile(suffix=".mp3") as mp3_file:
        audio.export(mp3_file.name, format="mp3")
        audio = AudioSegment.from_mp3(mp3_file.name)
        with tempfile.NamedTemporaryFile(suffix=".wav") as wav_file:
            audio.export(wav_file.name, format="wav")
            with wave.open(wav_file.name, "rb") as wave_read:
                audio_data = wave_read.readframes(wave_read.getnframes())
                num_channels = wave_read.getnchannels()
                bytes_per_sample = wave_read.getsampwidth()
                sample_rate = wave_read.getframerate()
    return audio_data, num_channels, bytes_per_sample, sample_rate
