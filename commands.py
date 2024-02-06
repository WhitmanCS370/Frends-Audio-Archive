import simpleaudio as sa


def playAudio(filename):
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until sound has finished playing


def playAudioAsync(filename):
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    return play_obj


def playSequence(filenames):
    for fname in filenames:
        playAudio(str(fname))


def playParallel(filenames):
    play_objs = []
    for fname in filenames:
        play_objs.append(playAudioAsync(str(fname)))
    for play_obj in play_objs:
        play_obj.wait_done()
