"""This file holds the AudioMetadata class, which serves as a way for us to interact with metadata.

AudioMetadata objects will be retrieved and stored in storage.
"""

from pathlib import Path
import time


class AudioMetadata:
    """The AudioMetada class serves to store metadata.

    Attributes:
        file_path: A Path object with the path to the sound.
        name: String name of the sound.
        duration: An integer representing the duration of the sound in seconds.
        author: String author of the sound.
        tags: String set of tags.
        last_accessed: Integer storing the time that a sound was last accessed (as seconds since epoch).
    """

    def __init__(self, **kwargs):
        """Constructor.

        Args:
            **file_path: A Path object with the path to the sound.
            **name: String name of the sound.
            **duration: An integer representing the duration of the sound in seconds.
            **author: String author of the sound.
            **tags: String set of tags.
            **last_accessed: Integer storing the time that a sound was last accessed (as seconds since epoch).
        """
        self.file_path = Path(kwargs["filePath"])
        self.name = kwargs["name"]
        self.duration = kwargs["duration"]
        self.date_added = kwargs["dateAdded"]
        self.author = kwargs["author"]
        self.tags = kwargs["tags"]
        self.last_accessed = None
        self._updateLastAccessed()

    def _updateLastAccessed(self):
        self.last_accessed = int(time.time())

    def __str__(self):
        """Return string containing information in AudioMetadata object."""
        res = []
        for val, name in zip(
            [
                self.file_path,
                self.name,
                self.duration,
                time.strftime("%c", time.localtime(self.date_added)),
                self.author,
                time.strftime("%c", time.localtime(self.last_accessed)),
            ],
            [
                "file path",
                "name",
                "duration",
                "date added",
                "author",
                "last accessed",
            ],
        ):
            res.append(f"{name}: {val}")
        res.append(f"tags: {', '.join(self.tags)}")
        return ("\n".join(res)) + "\n"
