"""This module holds a CLI for the audio archive."""

import argparse
import pathlib
from dummy_cache import DummyCache
from commands import *
from sqlite_storage import Sqlite
from storage_commander import StorageCommander


class Cli:
    """CLI for the audio archive.

    Attributes:
        commander: A Commander object, such as the one in commander.py.
    """

    def __init__(self, commander):
        """Constructor.

        This function assembles the argument parsers for different subcommands.

        Args:
            commander: A Commander object, such as the one in commander.py.
        """
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
            help="play all sounds simultaneously",
        )

        play_parser.add_argument(
            "-s",
            "--speed",
            type=float,
            help="float playback speed for audio (default: 1.0). NOTE: You must have FFmpeg installed in order to change the speed",
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
            "names", type=str, nargs="+", help="names of sounds to play"
        )

        add_parser = subparsers.add_parser(
            "add", description="Add files to audio archive"
        )
        add_parser.add_argument("filename", type=pathlib.Path, help="file to add")
        add_parser.add_argument(
            "-n", "--name", type=str, help="name of sound", default=None
        )

        list_parser = subparsers.add_parser(
            "list", description="Show files in audio archive"
        )

        rename_parser = subparsers.add_parser(
            "rename", description="Rename file in audio archive"
        )
        rename_parser.add_argument("name", type=str, help="name of sound")
        rename_parser.add_argument("new_name", type=str, help="new name for sound")

        clean_parser = subparsers.add_parser(
            "clean",
            description="Remove all sounds from archive that do not have an associated file",
        )

    def _handlePlay(self, args):
        kwargs = {
            "speed": args.speed,
            "volume": args.volume,
            "reverse": args.reverse,
        }
        try:
            if args.parallel:
                self.commander.playParallel(args.names, **kwargs)
            else:
                self.commander.playSequence(args.names, **kwargs)
        except NameMissing as e:
            print(f"Error: {e}")

    def _handleList(self):
        for sound in self.commander.getSounds():
            print(sound)

    def _handleRename(self, args):
        try:
            self.commander.rename(str(args.name), str(args.new_name))
        except NameMissing:
            print(f"{str(args.name)} does not exist in the archive.")
        except NameExists:
            print(
                f"There is already a sound named {str(args.new_name)} in the archive."
            )

    def _handleAdd(self, args):
        try:
            self.commander.addSound(args.filename, args.name)
        except NameExists:
            if args.name is None:
                print(
                    f"Invalid filename - the name already exists in the database.  Hint: Try providing a custom name with -n or --name."
                )
            else:
                print(
                    f"There is already a sound named {str(args.name)} in the archive."
                )
        except FileNotFoundError:
            print(f"{args.filename} is not a valid path to a file.")

    def _handleClean(self):
        self.commander.clean()

    def execute_command(self):
        """Parses arguments and calls appropriate function to handle command."""
        args = self.parser.parse_args()

        match args.command:
            case "play":
                self._handlePlay(args)
            case "list":
                self._handleList()
            case "rename":
                self._handleRename(args)
            case "add":
                self._handleAdd(args)
            case "clean":
                self._handleClean()


if __name__ == "__main__":
    try:
        storage = StorageCommander(DummyCache(), Sqlite())
    except FileNotFoundError as f:
        print(f"Error: {f}")
        print("See README.md for initialization instructions")
    else:
        commander = Commander(storage)
        cli = Cli(commander)
        cli.execute_command()
