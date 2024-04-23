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
        last_played: Integer seconds since epoch since last played.
        play_count: Integer number of times the sound has been played.
    """

    def __init__(self, **kwargs):
        """Constructor.

        Args:
            **file_path: A Path object with the path to the sound.
            **name: String name of the sound.
            **duration: An integer representing the duration of the sound in seconds.
            **author: String author of the sound.
            **tags: String set of tags.
            **last_played: Integer seconds since epoch since last played.
            **play_count: Integer number of times the sound has been played.
        """
        self.file_path = Path(kwargs["file_path"])
        self.name = kwargs["name"]
        self.duration = kwargs["duration"]
        self.date_added = kwargs["date_added"]
        self.last_played = kwargs["last_played"]
        self.author = kwargs["author"]
        self.tags = kwargs["tags"]
        self.play_count = kwargs["play_count"]

    def __eq__(self, other):
        """Equal dunder method.

        Two AudioObjects are the same if their name is the same.
        """
        return self.name == other.name

    def __str__(self):
        """Return string containing information in AudioMetadata object."""
        res = []
        last_played = (
            "Never"
            if self.last_played is None
            else time.strftime("%c", time.localtime(self.last_played))
        )
        date_added = time.strftime("%c", time.localtime(self.date_added))
        for val, name in zip(
            [
                self.file_path,
                self.name,
                self.duration,
                date_added,
                self.author,
                last_played,
                self.play_count,
            ],
            [
                "file path",
                "name",
                "duration",
                "date added",
                "author",
                "last played",
                "play count",
            ],
        ):
            res.append(f"{name}: {val}")
        tags_list = sorted(list(self.tags))
        res.append(f"tags: {', '.join(tags_list)}")
        return ("\n".join(res)) + "\n"
