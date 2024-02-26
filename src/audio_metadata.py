import time
import wave


class AudioMetadata:
    """
    This class is for use with a cache (not yet implemented)
    """

    def __init__(self, **kwargs):
        self.file_path = kwargs["filePath"]
        self.name = kwargs["name"]
        self.duration = kwargs["duration"]
        self.date_added = kwargs["dateAdded"]
        self.author = kwargs["author"]
        self.tags = kwargs["tags"]
        self.last_accessed = None
        self.updateLastAccessed()

    def addTags(self, tagsToAdd):
        for tag in tagsToAdd:
            self.tags.append(tag)

    # derives the name from the file path for naming the file
    def removeChars(self, string):
        returnVal = ""
        for c in reversed(string[0:-4]):
            if c != "/":
                returnVal += c
            else:
                break
        return returnVal[::-1]

    def setAuthor(self, author):
        self.author = author

    # should fetch date added from the database
    def getDateAdded(self, dateAdded):
        raise NotImplementedError("Needs to be derived from database")

    def setDuration(self):
        # get the duration
        with wave.open(self.file_path, "rb") as wave_read:
            self.duration = int(wave_read.getnframes() / wave_read.getframerate())

    def updateLastAccessed(self):
        self.last_accessed = time.time()

    def __str__(self):
        for val, name in zip(
            [
                self.file_path,
                self.name,
                self.duration,
                self.date_added,
                self.author,
                self.last_accessed,
                self.tags,
            ],
            [
                "file path",
                "name",
                "duration",
                "date added",
                "author",
                "last accessed",
                "tags",
            ],
        ):
            print(f"{name}: {val}")
