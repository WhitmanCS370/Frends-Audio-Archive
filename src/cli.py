import argparse
import commands
import pathlib


class Cli:
    def __init__(self, commander):
        self.commander = commander
        self.parser = argparse.ArgumentParser(description="Audio archive.")
        # since we want to have subself.commander, we create a subparser
        # by specifying dest="command", args.command will now hold the name of
        # the command
        subparsers = self.parser.add_subparsers(dest="command")
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
            "-s",
            "--speed",
            type=float,
            help="float playback speed for audio (default: 1.0)",
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

        list_parser = subparsers.add_parser(
            "list", description="Show files in audio archive"
        )

        rename_parser = subparsers.add_parser(
            "rename", description="Rename file in audio archive"
        )
        rename_parser.add_argument("filename", type=pathlib.Path, help="File to rename")
        rename_parser.add_argument(
            "new_name", type=pathlib.Path, help="New name for file"
        )

    def execute_command(self):
        args = self.parser.parse_args()

        match args.command:
            case "play":
                kwargs = {
                    "speed": args.speed,
                    "volume": args.volume,
                    "reverse": args.reverse,
                }
                fnames = [str(fname) for fname in args.audio_files]
                if args.parallel:
                    self.commander.playParallel(fnames, **kwargs)
                else:
                    self.commander.playSequence(fnames, **kwargs)
            case "list":
                for sound in self.commander.getSounds():
                    print(sound)
            case "rename":
                self.commander.rename(str(args.filename), str(args.new_name))


if __name__ == "__main__":
    commander = commands.Commander()
    cli = Cli(commander)
    cli.execute_command()
