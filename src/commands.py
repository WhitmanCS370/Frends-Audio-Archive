import os
import simpleaudio as sa
import wave
import numpy as np
import audioop


def playAudio(filename, reverse=False, volume=None, speed=None):
    wave_obj = sa.WaveObject.from_wave_file(filename)
    if reverse:
        audio_data = np.array(wave_obj.audio_data)
        wave_obj = sa.WaveObject(audioop.reverse(audio_data, int(wave_obj.bytes_per_sample)), wave_obj.num_channels, wave_obj.bytes_per_sample, wave_obj.sample_rate)

    if volume is not None:
        wave_obj = changeVolume(filename, volume)

    if speed is not None and speed > 0:
        raise NotImplementedError
        # wave_obj = changeSpeed(wave_obj, speed)
    
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
    wave_read = wave.open(filename, 'rb')
    sample_width = wave_read.getsampwidth()
    sample_rate = wave_read.getframerate()

    audio_data = np.frombuffer(wave_read.readframes(wave_read.getnframes()), dtype=np.int16)
    audio_data = (audio_data * volume).astype(np.int16)
    audio_data = np.clip(audio_data, -32768, 32767)

    wave_obj = sa.WaveObject(audio_data.tobytes(), bytes_per_sample=sample_width, sample_rate=sample_rate)

    return wave_obj
