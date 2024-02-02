import argparse
import pathlib
import simpleaudio as sa

parser = argparse.ArgumentParser(description="Play audio files.")
# nargs='+' means that we expect at least one argument.
parser.add_argument('audio_files', type=pathlib.Path, nargs='+',
                    help="audio files to play")
args = parser.parse_args()

def playAudio(filePath):
    filename = filePath
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until sound has finished playing

for fname in args.audio_files:
    playAudio(str(fname))
