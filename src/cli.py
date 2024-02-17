import argparse
import commands
import pathlib


parser = argparse.ArgumentParser(description="Audio archive.")
# since we want to have subcommands, we create a subparser
# by specifying dest="command", args.command will now hold the name of
# the command
subparsers = parser.add_subparsers(dest="command")
# we define a subcommand like this
play_parser = subparsers.add_parser("play", description="Play audio files")
# action="store_true" means that args.parallel will be True when -p is specified
play_parser.add_argument(
    "-p",
    "--parallel",
    action="store_true",
    help="play all files simultaneously",
)

play_parser.add_argument(
    "-s", "--speed", type=float, help="float playback speed for audio (default: 1.0)"
)

play_parser.add_argument(
    "-r", "--reverse", action="store_true", help="play the sounds in reverse"
)

play_parser.add_argument(
    "-v",
    "--volume",
    type=float,
    help="float playback volume for audio (default: 1.0)",
)

# nargs='+' means that we expect at least one argument
play_parser.add_argument(
    "audio_files", type=pathlib.Path, nargs="+", help="audio files to play"
)

list_parser = subparsers.add_parser("list", description="Show files in audio archive")

rename_parser = subparsers.add_parser(
    "rename", description="Rename file in audio archive"
)
rename_parser.add_argument("filename", type=pathlib.Path, help="File to rename")
rename_parser.add_argument("new_name", type=pathlib.Path, help="New name for file")


args = parser.parse_args()

match args.command:
    case "play":
        kwargs = {"speed": args.speed, "volume": args.volume, "reverse": args.reverse}
        fnames = [str(fname) for fname in args.audio_files]
        if args.parallel:
            commands.playParallel(fnames, **kwargs)
        else:
            commands.playSequence(fnames, **kwargs)
    case "list":
        for sound in commands.getSounds():
            print(sound)
    case "rename":
        commands.rename(str(args.filename), str(args.new_name))
