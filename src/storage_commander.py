from pathlib import Path
import time
import wave


class StorageCommander:
    def __init__(self, cache, database):
        self.cache = cache
        self.database = database

    def addSound(self, file_path, name=None, author=None):
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError()
        if name is None:
            # convert file_path to name of file without extension
            name = path.stem
        with wave.open(file_path, "rb") as wave_read:
            duration = int(wave_read.getnframes() / wave_read.getframerate())
        cur_time = int(time.time())
        self.database.add_sound(file_path, name, duration, cur_time, author)
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

    def getSounds(self):
        # skip cache
        pass

    def rename(self, old_name, new_name):
        self.database.rename(old_name, new_name)
        self.cache.rename(old_name, new_name)

    def addTag(self, name, tag):
        self.cache.addTag(name, tag)
        self.database.addTag(name, tag)

    def removeTag(self, name, tag):
        self.cache.removeTag(name, tag)
        self.database.removeTag(name, tag)
