class StorageCommander:
    def __init__(self, cache, database):
        self.cache = cache
        self.database = database

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
