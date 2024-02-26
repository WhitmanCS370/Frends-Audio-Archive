from pathlib import Path
from shutil import copyfile, move
import time
import wave


class StorageCommander:
    def __init__(self, cache, database, base_directory="sounds/"):
        self.cache = cache
        self.database = database
        self.base_directory = Path(base_directory)

    def addSound(self, file_path, name=None, author=None):
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError()
        if name is None:
            # convert file_path to name of file without extension
            name = path.stem
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

    def getByName(self, name):
        audio = self.cache.getByName(name)
        if audio is not None:
            return audio
        audio = self.database.getByName(name)
        self.cache.cache(audio)

    def getByTags(self, tags):
        audios = self.cache.getByTags(tags)
        if audios is not None:
            return audios
        audios = self.database.getByTags(tags)
        for audio in audios:
            self.cache.cache(audio)

    def getAll(self):
        return self.database.getAll()

    def rename(self, old_name, new_name):
        self.database.rename(old_name, new_name)
        self.cache.rename(old_name, new_name)

    def addTag(self, name, tag):
        self.cache.addTag(name, tag)
        self.database.addTag(name, tag)

    def removeTag(self, name, tag):
        self.cache.removeTag(name, tag)
        self.database.removeTag(name, tag)
