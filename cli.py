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
    help="specify -p to play all files simultaneously",
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
        if args.parallel:
            commands.playParallel([str(fname) for fname in args.audio_files])
        else:
            commands.playSequence([str(fname) for fname in args.audio_files])
    case "list":
        for sound in commands.getSounds():
            print(sound)
    case "rename":
        commands.rename(str(args.filename), str(args.new_name))
