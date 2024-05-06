"""This module holds a CLI for the audio archive."""

import argparse
import pathlib
from playback_options import PlaybackOptions
from pydub.exceptions import CouldntDecodeError
from commander import *


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
        self.parser = argparse.ArgumentParser(description="Audio archive")
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

        play_parser.add_argument(
            "--start_percent",
            type=float,
            help="The start position of the audio as a percent. Ranges from 0 to 1, where 0 removes nothing from the start, and 1 removes everything. (default: 0)",
        )

        play_parser.add_argument(
            "--end_percent",
            type=float,
            help="The end position of the audio as a percent. Ranges from 0 to 1, where 1 removes nothing from the end, and 0 removes everything. (default: 1)",
        )

        play_parser.add_argument(
            "--start_sec",
            type=float,
            help="The start position (in seconds) to start the audio crop. (default: 0)",
        )

        play_parser.add_argument(
            "--end_sec",
            type=float,
            help="The end position (in seconds) to end the audio crop. (default: 0)",
        )

        play_parser.add_argument(
            "--save",
            type=str,
            help="Saves the audio to a file instead of playing it",
        )

        play_parser.add_argument(
            "-t", "--transpose", type=int, help="transposes the sound by n semitones"
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

        remove_parser = subparsers.add_parser(
            "remove",
            description="Remove sounds from the audio archive. NOTE: This is permanent and cannot be undone",
        )
        remove_parser.add_argument("name", type=str, help="sound to remove")

        tag_parser = subparsers.add_parser(
            "tag",
            description="Add or remove tags from a sound",
            help="tag [name] [tag1, tag2, ...] adds tags by default - specify -r to remove the tags",
        )
        tag_parser.add_argument(
            "name", type=str, help="name of sound to add or remove tag from"
        )
        tag_parser.add_argument(
            "tags", type=str, nargs="+", help="tags to add or remove"
        )
        tag_parser.add_argument(
            "-r",
            "--remove",
            action="store_true",
            help="specify to remove the tag from the sound",
        )

        list_parser = subparsers.add_parser(
            "list",
            description="Show sounds in audio archive",
            help="Shows all sounds by default - specify tags to show sounds with tags",
        )
        list_parser.add_argument(
            "tags", type=str, nargs="*", help="Show sounds with tags"
        )

        rename_parser = subparsers.add_parser(
            "rename", description="Rename file in audio archive"
        )

        find_parser = subparsers.add_parser(
            "find", description="Fuzzy search for sounds in audio archive. Find [n] sounds with the closest name to [name]"
        )
        find_parser.add_argument("name", type=str, help="Name to search for")
        find_parser.add_argument(
            "n",
            type=int,
            nargs="?",
            default=10,
            help="Maximum number of results to return (default: 10)",
        )

        rename_parser.add_argument("name", type=str, help="name of sound")
        rename_parser.add_argument("new_name", type=str, help="new name for sound")

        clean_parser = subparsers.add_parser(
            "clean",
            description="Remove all sounds from archive that do not have an associated file",
        )

    def executeCommand(self):
        """Parses arguments and calls appropriate function to handle command.

        This uses a dynamic dispatch by using getattr() to find the function from
        the command name.
        """
        args = self.parser.parse_args()
        method_name = f"_handle{args.command.capitalize()}"
        handle_function = getattr(self, method_name)
        handle_function(args)

    def _handlePlay(self, args):
        try:
            playback_options = PlaybackOptions(
                speed=args.speed,
                volume=args.volume,
                reverse=args.reverse,
                start_percent=args.start_percent,
                end_percent=args.end_percent,
                start_sec=args.start_sec,
                end_sec=args.end_sec,
                save=args.save,
                transpose=args.transpose,
                parallel=args.parallel,
            )
            self.commander.playAudio(args.names, playback_options)

        except ValueError as e:
            print(f"Error: {e}")
        except NameMissing as e:
            print(f"Error: {e}")
        except FileNotFoundError as e:
            print(f"Error: {e}")
        except NameExists as e:
            print(
                f"{args.save} already exists in the archive - edited version not saved"
            )

    def _handleList(self, args):
        # TODO: Consider a better way to handle filtering by tags.
        if len(args.tags) == 0:
            sounds = self.commander.storage.getAll()
        else:
            sounds = self.commander.storage.getByTags(args.tags)

        for sound in sounds:
            print(sound)

    def _handleFind(self, args):
        sounds = self.commander.storage.fuzzySearch(args.name, args.n)
        for sound in sounds:
            print(sound)

    def _handleRename(self, args):
        try:
            self.commander.storage.rename(str(args.name), str(args.new_name))
        except NameMissing:
            print(f"{str(args.name)} does not exist in the archive")
        except NameExists:
            print(
                f"There is already a sound named {str(args.new_name)} in the archive"
            )

    def _handleAdd(self, args):
        try:
            self.commander.storage.addSound(args.filename, args.name)
        except NameExists:
            if args.name is None:
                print(
                    f"Invalid filename - the name already exists in the database.  Hint: Try providing a custom name with -n or --name"
                )
            else:
                print(
                    f"There is already a sound named {str(args.name)} in the archive"
                )
        except FileNotFoundError:
            print(f"{args.filename} is not a valid path to a file")
        except ValueError as e:
            print(e)
        except CouldntDecodeError:
            print(
                f"Error: Unsupported file format. ffmpeg is required for many file formats"
            )

    def _handleRemove(self, args):
        try:
            self.commander.storage.removeSound(args.name)
        except NameMissing:
            print(f"{args.name} does not exist in the archive")

    def _handleTag(self, args):
        try:
            for tag in args.tags:
                if args.remove:
                    self.commander.storage.removeTag(args.name, tag)
                else:
                    self.commander.storage.addTag(args.name, tag)
        except NameMissing:
            print(f"{args.name} does not exist in the archive")
        except ValueError as e:
            print(e)

    def _handleClean(self, _args):
        self.commander.storage.clean()


if __name__ == "__main__":
    try:
        commander = Commander()
    except FileNotFoundError as f:
        print(f"Error: {f}")
        print("See README.md for initialization instructions")
    else:
        cli = Cli(commander)
        cli.executeCommand()
