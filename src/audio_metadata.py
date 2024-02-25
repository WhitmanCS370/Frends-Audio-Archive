from scipy.io import wavfile
import time


class AudioMetadata:
    """
    This class is for use with a cache (not yet implemented)
    """

    def __init__(self, **kwargs):
        self.location = kwargs["filePath"]
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

        sample_rate, data = wavfile.read(self.location)
        len_data = len(data)
        self.duration = len_data / sample_rate

    def updateLastAccessed(self):
        self.last_accessed = time.time()

    def testAttributes(self):
        print(self.location)
        print(self.name)
        print(self.duration)
        print(self.date_added)
        print(self.last_accessed)
        print(self.author)
        print(self.tags)
