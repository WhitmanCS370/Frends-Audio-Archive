import argparse
import commands
import pathlib


def main():
    parser = argparse.ArgumentParser(description="Play audio files.")
    # action="store_true" means that args.parallel will be True when -p is specified
    parser.add_argument(
        "-p",
        "--parallel",
        action="store_true",
        help="specify -p to play all files simultaneously",
    )
    # nargs='+' means that we expect at least one argument
    parser.add_argument(
        "audio_files", type=pathlib.Path, nargs="+", help="audio files to play"
    )
    args = parser.parse_args()

    if args.parallel:
        commands.playParallel([str(fname) for fname in args.audio_files])
    else:
        commands.playSequence([str(fname) for fname in args.audio_files])


if __name__ == "__main__":
    main()
