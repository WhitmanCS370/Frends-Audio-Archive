"""Manage interactions with storage for the audio archive.
"""

import tempfile
from pathlib import Path
import soundfile
from pydub import AudioSegment
from shutil import copyfile, move
import time
import wave
from constants import *
from storage_exceptions import *


def _processTag(tag):
    """Strip whitespace and turn to lowercase."""
    return tag.lower().strip()


class StorageCommander:
    """Manage interactions with audio archive storage

    This class functions as a bridge between the commander and database.  There
    is some processing that must happen before audio metadata is stored, such as
    moving files around and normalizing tags, and this class handles that.

    Attributes:
        database: A database object - ex: sqlite_storage.py.
        base_directory: A Path to the directory in which sounds are stored.
    """

    def __init__(self, database, base_directory="sounds/"):
        """Constructor.

        Args:
            database: A database object - ex: sqlite_storage.py.
            base_directory: A String with a path to the directory in which sounds are stored.
        """
        self.database = database
        self.base_directory = Path(base_directory)

    def addSound(self, file_path, name=None, author=None):
        """Add a sound to the database.

        If the file_path is not in the base_directory, the file is moved to the base_directory.
        If the file_path is in the directory but the stem does not match the name parameter,
        the file is renamed to the name parameter.

        Args:
            file_path: A String with a path to the sound to add.
            name: Either a string with the name for the sound or None.
                If the name is None, it will default to the stem of the file path.
            author: Either a string with the name of the author or None.

        Returns:
            A boolean representing whether the sound was successfully added.

        Raises:
            NameExists: [name] is already in the database.
            FileNotFoundError: [file_path] is not a valid path to a file.
            ValueError: [name] or [author] is too long.
            pydub.exceptions.CouldntDecodeError: Unsupported file format.
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Path does not exist: {file_path}")
        if name is None:
            # convert file_path to name of file without extension
            name = path.stem
        if len(name) > MAX_SOUND_NAME_LENGTH:
            raise ValueError(
                f"Sound name must be less than {MAX_SOUND_NAME_LENGTH} characters."
            )
        if author is not None and len(author) > MAX_AUTHOR_LENGTH:
            raise ValueError(
                f"Author name must be less than {MAX_AUTHOR_LENGTH} characters."
            )
        if self._soundExists(name):
            raise NameExists(f"{name} already exists")

        new_path = self.base_directory / f"{name}.wav"

        if new_path != path:
            if path.suffix != ".wav":
                self._convertToWavAndAdd(path, new_path)
            elif (
                path.parent != self.base_directory
            ):  # copy file if we're adding it from outside sounds/
                copyfile(path, new_path)
            else:  # if it's already in the sounds/ directory, move the file
                move(path, new_path)

        with wave.open(str(new_path), "rb") as wave_read:
            duration = int(wave_read.getnframes() / wave_read.getframerate())
        cur_time = int(time.time())
        self.database.addSound(str(new_path), name, duration, cur_time, author)
        return True

    def removeSound(self, name):
        """Remove a sound from the database.

        This also removes the file from the base_directory.

        Args:
            name: String name of sound.

        Returns:
            A boolean representing whether the operation was successful.

        Raises:
            NameMissing: [name] does not exist in the database.
        """
        sound = self.getByName(name)
        self.database.removeByName(name)
        sound.file_path.unlink(missing_ok=True)  # remove file
        return True

    def getByName(self, name):
        """Retrieve a sound from storage.

        Args:
            name: String name of sound.

        Returns:
            An AudioMetadata object for the sound with the given name.

        Raises:
            NameMissing: [name] does not exist in the database.
        """
        return self.database.getByName(name)

    def updateLastPlayed(self, name):
        """Sets the last played time for a sound.

        Args:
            name: String name of sound.

        Raises:
            NameMissing: [name] does not exist in the database.
        """
        self.database.updateLastPlayed(name, int(time.time()))

    def incrementPlayCount(self, name):
        """Increases the play count for a sound by 1.

        Args:
            name: String name of sound.

        Raises:
            NameMissing: [name] does not exist in the database.
        """
        self.database.incrementPlayCount(name)

    def getByTags(self, tags):
        """Get all sounds associated with the given tags.

        Args:
            tags: String list of tags.

        Returns:
            A list AudioMetadata objects for all sounds associated with the given tags.
        """
        tags = [_processTag(tag) for tag in tags]
        # remove duplicates
        tags = list(set(tags))
        return self.database.getByTags(tags)

    def getAll(self):
        """Get all sounds from the storage (as AudioMetadata objects)."""
        return self.database.getAll()

    def fuzzySearch(self, target, n):
        """Get n sounds with smallest edit distance when compared to target.

        Args:
            target: String to search for.
            n: Int maximum number of sounds to return.

        Returns:
            A list of AudioMetadata objects in non-descending order of edit distance
            from target. If there are fewer than n sounds in the archive, all sounds
            will be returned.
        """
        return self.database.fuzzySearch(target, n)

    def rename(self, old_name, new_name):
        """Rename a sound.

        Args:
            old_name: String old name of sound.
            new_name: String new name for sound (must not already exist).
            new_path: String new file path of the sound.

        Returns:
            A boolean representing whether the operation was successful.

        Raises:
            NameExists: [new_name] already exists in the database.
            NameMissing: [old_name] does not exist in the database.
        """
        if not self._soundExists(old_name):
            raise NameMissing(f"{old_name} does not exist")
        if self._soundExists(new_name):
            raise NameExists(f"{new_name} already exists")
        sound = self.getByName(old_name)
        new_path = Path(self.base_directory, f"{new_name}.wav")
        move(sound.file_path, new_path)
        sound.file_path = new_path
        self.database.rename(old_name, new_name, str(new_path))
        return True

    def addTag(self, name, tag):
        """Add a tag to a sound.

        Args:
            name: String name of sound to add a tag to.
            tag: String name of tag.

        Raises:
            NameMissing: [name] isn't in the database.
            ValueError: [tag] is too long.
        """
        tag = _processTag(tag)
        if len(tag) > MAX_TAG_LENGTH:
            raise ValueError(f"Tag must be shorter than {MAX_TAG_LENGTH} characters.")
        self.database.addTag(name, tag)

    def removeTag(self, name, tag):
        """Remove a tag from a sound.

        Args:
            name: String name of sound to remove a tag from.
            tag: String name of tag.

        Raises:
            NameMissing: [name] isn't in the database.
        """
        tag = _processTag(tag)
        self.database.removeTag(name, tag)

    def clean(self):
        """Remove all sounds from the database without an associated file.

        Returns:
            A list of AudioMetadata objects that were removed.
        """
        sounds = self.getAll()
        removed_sounds = []
        for sound in sounds:
            if not sound.file_path.exists():
                self.removeSound(sound.name)
                removed_sounds.append(sound)

        return removed_sounds

    def _soundExists(self, name):
        """Returns if a sound exists in the database."""
        try:
            self.database.getByName(name)
            return True
        except NameMissing:
            return False

    def _convertToWavAndAdd(self, path, new_path):
        """Converts a sound file to a wav and moves it to the base directory.

        ffmpeg is needed for most file formats.

        Args:
            path: Path object leading to sound.
            new_path: New path to put sound at.
        """
        audio = AudioSegment.from_file(path)
        with tempfile.TemporaryDirectory() as temp_dir:
            path = str(Path(temp_dir, "sound.wav"))
            audio.export(path, format="wav")
            data, samplerate = soundfile.read(path)
            soundfile.write(str(new_path), data, samplerate)
