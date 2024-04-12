"""This module provides functions for working with a Sqlite database."""

from pathlib import Path
import sqlite3
from audio_metadata import AudioMetadata
from storage_exceptions import *


class Sqlite:
    """Interact with sqlite database for audio archive.

    Commands that directly interact with the database use the SqliteManager
    context manager.

    Attributes:
        db_name: String name of the database (representing path to sqlite db file).
    """

    def __init__(self, db_name="audio_archive.db"):
        """Constructor.

        Args:
            db_name: String name of the database (representing path to sqlite db file).

        Raises:
            FileNotFoundError: The file [db_name] does not exist.
        """
        if not Path(db_name).exists():
            raise FileNotFoundError("No database file found")
        self.db_name = db_name

    def addSound(self, file_path, name, duration, cur_time, author=None):
        """Adds a sound to the database if there is not already a sound with the given name.

        Args:
            file_path: String path to sound.
            name: String name of sound.
            duration: Int length of sound (in seconds).
            date_added: Int number of seconds since epoch.
            last_accessed: Int number of seconds since epoch.
            author: String name of author.

        Raises:
            NameExists: [name] already exists in the database.
        """
        query = """INSERT INTO sounds (file_path, name, duration, date_added, last_accessed, author)
        VALUES (?, ?, ?, ?, ?, ?);"""
        with SqliteManager(self.db_name) as m:
            try:
                m.cur.execute(
                    query, (file_path, name, duration, cur_time, cur_time, author)
                )
                m.con.commit()
            except sqlite3.IntegrityError as e:
                raise NameExists(f"{name} already exists in database\n{e}")

    def removeByName(self, name):
        """Remove a sound from the database.

        Args:
            name: String name of sound.

        Raises:
            NameMissing: [name] does not exist in the database.
        """
        query = "DELETE FROM sounds WHERE name = ?;"
        with SqliteManager(self.db_name) as m:
            m.cur.execute(query, (name,))
            if m.cur.rowcount == 0:
                raise NameMissing(f"{name} does not exist in database")
            m.con.commit()

    def getByName(self, name):
        """Retrieve a sound from the database.

        Args:
            name: String name of sound.

        Returns:
            An AudioMetadata object for the sound with the given name.

        Raises:
            NameMissing: [name] does not exist in the database.
        """
        query = "SELECT * FROM sounds WHERE name = ?;"
        with SqliteManager(self.db_name) as m:
            res = m.cur.execute(query, (name,))
            data = res.fetchone()
        if data is None:
            raise NameMissing(f"{name} does not exist in database")
        return self._recordToAudioMetadata(data)

    def getByTags(self, tags):
        """Get all sounds associated with the given tags.

        Args:
            tags: String list of tags.

        Returns:
            A list AudioMetadata objects for all sounds associated with the given tags.
        """
        tags = list(set(tags))  # remove duplicates
        tags = ", ".join(tags)
        query = """SELECT id, file_path, name, duration, date_added, last_accessed, author
        FROM sounds s
        LEFT JOIN tags t ON s.id = t.sound_id
        WHERE t.tag IN (?);"""
        with SqliteManager(self.db_name) as m:
            sounds = m.cur.execute(query, (tags,)).fetchall()
        return [self._recordToAudioMetadata(row) for row in sounds]

    def getAll(self):
        """Get all sounds from the database (as AudioMetadata objects)."""
        query = "SELECT * FROM sounds ORDER BY name;"
        with SqliteManager(self.db_name) as m:
            res = m.cur.execute(query).fetchall()
        return [self._recordToAudioMetadata(row) for row in res]

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
        # create a list of (edit distance, sound) tuples to sort
        # I chose to do this rather than providing a key for the sort function to avoid
        # calling _editDistance for every comparison.
        sounds = [(_editDistance(sound.name, target), sound) for sound in self.getAll()]
        sounds.sort()
        sounds = [sound[1] for sound in sounds]  # change tuple back to sound
        if len(sounds) <= n:
            return sounds
        return sounds[:n]

    def rename(self, old_name, new_name, new_path):
        """Rename a sound.

        Args:
            old_name: String old name of sound.
            new_name: String new name for sound (must not already exist).
            new_path: String new file path of the sound.

        Raises:
            NameExists: [new_name] already exists in the database.
            NameMissing: [old_name] does not exist in the database.
        """
        query = """UPDATE sounds
        SET name = ?, file_path = ?
        WHERE name = ?;"""
        with SqliteManager(self.db_name) as m:
            try:
                m.cur.execute(query, (new_name, new_path, old_name))
            except sqlite3.IntegrityError:
                raise NameExists(f"{new_name} already in database")
            if m.cur.rowcount == 0:
                raise NameMissing(f"{old_name} does not exist in database")
            m.con.commit()

    def addTag(self, name, tag):
        """Add a tag to a sound.

        Args:
            name: String name of sound to add a tag to.
            tag: String name of tag.

        Raises:
            NameMissing: [name] isn't in the database.
        """
        sound_id = self._getSoundID(name)
        query = "INSERT INTO tags (tag, sound_id) VALUES (?, ?);"
        with SqliteManager(self.db_name) as m:
            m.cur.execute(query, (tag, sound_id))
            m.con.commit()

    def removeTag(self, name, tag):
        """Remove a tag from a sound.

        Args:
            name: String name of sound to remove a tag from.
            tag: String name of tag.

        Raises:
            NameMissing: [name] isn't in the database.
        """
        sound_id = self._getSoundID(name)
        query = "DELETE FROM tags WHERE sound_id = ? AND tag = ?;"
        with SqliteManager(self.db_name) as m:
            m.cur.execute(query, (sound_id, tag))
            m.con.commit()

    def _getTags(self, id):
        """Get all tags associated with a sound ID.

        Args:
            id: Int sound ID.

        Returns:
            A list of AudioMetadata objects associated with the ID.
        """
        query = "SELECT tag FROM tags WHERE sound_id = ?;"
        with SqliteManager(self.db_name) as m:
            res = m.cur.execute(query, (id,)).fetchall()
        return {data[0] for data in res}

    def _getSoundID(self, name):
        """Get the ID associated with a sound.

        Args:
            name: String name of sound.

        Returns:
            Integer id associated with [name].

        Raises:
            NameMissing: [name] isn't in the database.
        """
        query = "SELECT id FROM sounds WHERE name = ?"
        with SqliteManager(self.db_name) as m:
            res = m.cur.execute(query, (name,)).fetchone()
            if len(res) == 0:
                raise NameMissing(f"{name} does not exist in database")
        return res[0]

    def _recordToAudioMetadata(self, record):
        """Convert one row from the sounds table to an AudioMetadata object."""
        tags = self._getTags(record[0])
        return AudioMetadata(
            filePath=record[1],
            name=record[2],
            duration=record[3],
            dateAdded=record[4],
            lastAccessed=record[5],
            author=record[6],
            tags=tags,
        )


class SqliteManager:
    """Provide context manager for working with sqlite database."""

    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        return self

    def __exit__(self, *_args):
        self.con.close()


def _editDistance(word1, word2):
    """Find edit distance from word1 to word2.

    Copy and pasted from https://leetcode.com/problems/edit-distance/submissions/904968575/
    because why write your own tests when they're there for you 😀
    """
    n, m = len(word1), len(word2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for i in range(m + 1):
        dp[0][i] = i

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]) + 1
    return dp[-1][-1]
