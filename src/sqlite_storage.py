import sqlite3
from audio_metadata import AudioMetadata


class SqliteManager:
    """Provide context manager for working with sqlite database"""

    def __init__(self, db_name):
        self.db_name = db_name

    def __enter__(self):
        self.con = sqlite3.connect(self.db_name)
        self.cur = self.con.cursor()
        return self

    def __exit__(self, *_args):
        self.con.close()


class Sqlite:
    """Interact with sqlite database for audio archive

    Commands that directly interact with the database use the SqliteManager
    context manager.
    """

    def __init__(self, db_name="audio_archive.db"):
        self.db_name = db_name

    def addSound(self, file_path, name, duration, cur_time, author=None):
        query = """INSERT INTO sounds (file_path, name, duration, date_added, last_accessed, author)
        VALUES (?, ?, ?, ?, ?, ?);"""
        with SqliteManager(self.db_name) as m:
            m.cur.execute(
                query, (file_path, name, duration, cur_time, cur_time, author)
            )
            m.con.commit()

    def removeByName(self, name):
        query = "DELETE FROM sounds WHERE name = ?;"
        with SqliteManager(self.db_name) as m:
            m.cur.execute(query, (name,))
            m.con.commit()

    def getByName(self, name):
        query = "SELECT * FROM sounds WHERE name = ?;"
        with SqliteManager(self.db_name) as m:
            res = m.cur.execute(query, (name,))
            data = res.fetchone()
        if data is None:
            return None
        return self._recordToAudioMetadata(data)

    def getByTags(self, tags):
        tags = ", ".join(tags)
        query = """SELECT id, file_path, name, duration, date_added, last_accessed, author
        FROM sounds s
        LEFT JOIN tags t ON s.id = t.sound_id
        WHERE t.tag IN (?);"""
        with SqliteManager(self.db_name) as m:
            sounds = m.cur.execute(query, (tags,)).fetchall()
        return [self._recordToAudioMetadata(row) for row in sounds]

    def getAll(self):
        query = "SELECT * FROM sounds ORDER BY name;"
        with SqliteManager(self.db_name) as m:
            res = m.cur.execute(query).fetchall()
        return [self._recordToAudioMetadata(row) for row in res]

    def rename(self, old_name, new_name, new_path):
        query = """UPDATE sounds
        SET name = ?, file_path = ?
        WHERE name = ?;"""
        with SqliteManager(self.db_name) as m:
            m.cur.execute(query, (new_name, new_path, old_name))
            m.con.commit()

    def addTag(self, name, tag):
        sound_id = self._getSoundID(name)
        query = "INSERT INTO tags (tag, sound_id) VALUES (?, ?);"
        with SqliteManager(self.db_name) as m:
            m.cur.execute(query, (tag, sound_id))
            m.con.commit()

    def removeTag(self, name, tag):
        sound_id = self._getSoundID(name)
        query = "DELETE FROM tags WHERE sound_id = ? AND tag = ?;"
        with SqliteManager(self.db_name) as m:
            m.cur.execute(query, (sound_id, tag))
            m.con.commit()

    def _getTags(self, id):
        """returns tags associated with a sound id"""
        query = "SELECT tag FROM tags WHERE sound_id = ?;"
        with SqliteManager(self.db_name) as m:
            res = m.cur.execute(query, (id,)).fetchall()
        return [data[0] for data in res]

    def _getSoundID(self, name):
        query = "SELECT id FROM sounds WHERE name = ?"
        with SqliteManager(self.db_name) as m:
            res = m.cur.execute(query, (name,)).fetchone()[0]
        return res

    def _recordToAudioMetadata(self, record):
        """converts one from the sounds table to an AudioMetadata object"""
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
