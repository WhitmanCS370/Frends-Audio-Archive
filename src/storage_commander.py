import os
from pathlib import Path
from shutil import copyfile, move
import time
import wave


class StorageCommander:
    """Manage interactions with audio archive storage

    This class exists because we are implementing caching to reduce database queries.
    Both a cache and database object our provided during construction, and this class
    handles dispatching commands to the appropriate storage mechanism, as well as
    keeping the database, cache, and sounds directory in sync.
    """

    def __init__(self, cache, database, base_directory="sounds/"):
        self.cache = cache
        self.database = database
        self.base_directory = Path(base_directory)

    # returns false if the name is already in the audio archive
    def addSound(self, file_path, name=None, author=None):
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError()
        if name is None:
            # convert file_path to name of file without extension
            name = path.stem
        if self.database.getByName(name) is not None:
            # name already exists - don't add
            return False
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

    # returns true if the sound is successfully removed
    def removeSound(self, name):
        audio = self.getByName(name)
        if audio is None:
            return False
        self.database.removeByName(name)
        self.cache.removeByName(name)
        if os.path.exists(audio.file_path):
            os.remove(audio.file_path)
        return True

    def getByName(self, name):
        audio = self.cache.getByName(name)
        if audio is not None:
            return audio
        audio = self.database.getByName(name)
        self.cache.cache(audio)
        return audio

    def getByTags(self, tags):
        audios = self.cache.getByTags(tags)
        if audios is not None:
            return audios
        audios = self.database.getByTags(tags)
        for audio in audios:
            self.cache.cache(audio)
        return audios

    def getAll(self):
        return self.database.getAll()

    def rename(self, old_name, new_name):
        audio = self.getByName(old_name)
        if audio is None or self.getByName(new_name) is not None:
            return False
        new_path = os.path.join(self.base_directory, f"{new_name}.wav")
        move(audio.file_path, new_path)
        audio.file_path = new_path
        self.database.rename(old_name, new_name, new_path)
        self.cache.rename(old_name, new_name)
        return True

    def addTag(self, name, tag):
        self.cache.addTag(name, tag)
        self.database.addTag(name, tag)

    def removeTag(self, name, tag):
        self.cache.removeTag(name, tag)
        self.database.removeTag(name, tag)

    def clean(self):
        sounds = self.getAll()
        removed_sounds = []
        for sound in sounds:
            if not os.path.exists(sound.file_path):
                self.removeSound(sound.name)
                removed_sounds.append(sound)

        return removed_sounds
