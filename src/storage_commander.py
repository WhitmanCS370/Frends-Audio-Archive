"""Manage interactions with storage for the audio archive.

This class is needed because we wanted to use an in memory cache as well as a database.
It manages searching for sounds in the cache when possible and then falling back on
the database. This class also helps keep the database, cache, and sounds directory in sync.
"""

from pathlib import Path
from shutil import copyfile, move
import time
import wave
from storage_exceptions import *


class StorageCommander:
    """Manage interactions with audio archive storage

    This class exists because we are implementing caching to reduce database queries.
    Both a cache and database object our provided during construction, and this class
    handles dispatching commands to the appropriate storage mechanism, as well as
    keeping the database, cache, and sounds directory in sync.

    Attributes:
        cache: A cache object - ex: cache.py.
        database: A database object - ex: sqlite_storage.py.
        base_directory: A Path to the directory in which sounds are stored.
    """

    def __init__(self, cache, database, base_directory="sounds/"):
        """Constructor.

        Args:
            cache: A cache object - ex: cache.py.
            database: A database object - ex: sqlite_storage.py.
            base_directory: A String with a path to the directory in which sounds are stored.
        """

        self.cache = cache
        self.database = database
        self.base_directory = Path(base_directory)

    def addSound(self, file_path, name=None, author=None):
        """Add a sound to the cache and database.

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
        """
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Path does not exist: {file_path}")
        if name is None:
            # convert file_path to name of file without extension
            name = path.stem
        if self._soundExists(name):
            raise NameExists(f"{name} already exists")
        new_path = self.base_directory / f"{name}.wav"

        if new_path != path:
            # copy file if we're adding it from outside sounds/
            if path.parent != self.base_directory:
                copyfile(path, new_path)
            else:  # if it's already in the sounds/ directory, move the file
                move(path, new_path)

        with wave.open(str(new_path), "rb") as wave_read:
            duration = int(wave_read.getnframes() / wave_read.getframerate())
        cur_time = int(time.time())
        self.database.addSound(str(new_path), name, duration, cur_time, author)
        audio = self.getByName(name)
        self.cache.cache(audio)
        return True

    def removeSound(self, name):
        """Remove a sound from the database and cache.

        This also removes the file from the base_directory.

        Args:
            name: String name of sound.

        Returns:
            A boolean representing whether the operation was successful.

        Raises:
            NameMissing: [name] does not exist in the database.
        """
        audio = self.getByName(name)
        self.database.removeByName(name)
        self.cache.removeByName(name)
        audio.file_path.unlink(missing_ok=True)  # remove file
        return True

    def getByName(self, name):
        """Retrieve a sound from storage.

        Adds to the cache if not already present.

        Args:
            name: String name of sound.

        Returns:
            An AudioMetadata object for the sound with the given name.

        Raises:
            NameMissing: [name] does not exist in the database.
        """
        audio = self.cache.getByName(name)
        if audio is not None:
            return audio
        audio = self.database.getByName(name)
        self.cache.cache(audio)
        return audio

    def getByTags(self, tags):
        """Get all sounds associated with the given tags.

        Caches sounds that are not already cached.

        Args:
            tags: String list of tags.

        Returns:
            A list AudioMetadata objects for all sounds associated with the given tags.
        """
        audios = self.database.getByTags(tags)
        for audio in audios:
            self.cache.cache(audio)
        return audios

    def getAll(self):
        """Get all sounds from the storage (as AudioMetadata objects)."""
        return self.database.getAll()

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
        audio = self.getByName(old_name)
        new_path = Path(self.base_directory, f"{new_name}.wav")
        move(audio.file_path, new_path)
        audio.file_path = new_path
        self.database.rename(old_name, new_name, str(new_path))
        self.cache.rename(old_name, new_name)
        return True

    def addTag(self, name, tag):
        """Add a tag to a sound.

        Args:
            name: String name of sound to add a tag to.
            tag: String name of tag.

        Raises:
            NameMissing: [name] isn't in the database.
        """
        self.cache.addTag(name, tag)
        self.database.addTag(name, tag)

    def removeTag(self, name, tag):
        """Remove a tag from a sound.

        Args:
            name: String name of sound to remove a tag from.
            tag: String name of tag.

        Raises:
            NameMissing: [name] isn't in the database.
        """
        self.cache.removeTag(name, tag)
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
