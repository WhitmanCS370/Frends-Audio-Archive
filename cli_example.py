import argparse
import pathlib
import simpleaudio as sa

def playAudio(filename):
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    play_obj.wait_done()  # Wait until sound has finished playing

def playAudioAsync(filename):
    wave_obj = sa.WaveObject.from_wave_file(filename)
    play_obj = wave_obj.play()
    return play_obj

def main():
    parser = argparse.ArgumentParser(description="Play audio files.")
    # action="store_true" means that args.parallel will be True when -p is specified
    parser.add_argument("-p", "--parallel", action="store_true",
                        help="specify -p to play all files simultaneously")
    # nargs='+' means that we expect at least one argument
    parser.add_argument('audio_files', type=pathlib.Path, nargs='+',
                        help="audio files to play")
    args = parser.parse_args()

    if args.parallel:
        play_objs = []
        for fname in args.audio_files:
            play_objs.append(playAudioAsync(str(fname)))
        for play_obj in play_objs:
            play_obj.wait_done()
    else:
        for fname in args.audio_files:
            playAudio(str(fname))

if __name__ == "__main__":
    main()
