import sqlite3
from audio_metadata import AudioMetadata


def _manage_connection(f):
    def new_f(self, *args, **kwargs):
        con = sqlite3.connect(self.db_name)
        cur = con.cursor()
        res = f(self, con, cur, *args, **kwargs)
        con.close()
        return res

    return new_f


class Sqlite:
    def __init__(self, db_name="audio_archive.db"):
        self.db_name = db_name

    @_manage_connection
    def addSound(self, con, cur, file_path, name, duration, cur_time, author=None):
        query = """INSERT INTO sounds (file_path, name, duration, date_added, last_accessed, author)
        VALUES (?, ?, ?, ?, ?, ?);"""
        cur.execute(query, (file_path, name, duration, cur_time, cur_time, author))
        con.commit()

    @_manage_connection
    def removeByName(self, con, cur, name):
        query = "DELETE FROM sounds WHERE name = ?;"
        cur.execute(query, (name,))
        con.commit()

    @_manage_connection
    def getByName(self, _con, cur, name):
        res = cur.execute("SELECT * FROM sounds WHERE name = ?;", (name,))
        data = res.fetchone()
        if data is None:
            return None
        return self._recordToAudioMetadata(data)

    @_manage_connection
    def getByTags(self, _con, cur, tags):
        tags = ", ".join(tags)
        query = """SELECT id, file_path, name, duration, date_added, last_accessed, author
        FROM sounds s
        LEFT JOIN tags t ON s.id = t.sound_id
        WHERE t.tag IN (?);"""
        sounds = cur.execute(query, (tags,)).fetchall()
        return [self._recordToAudioMetadata(row) for row in sounds]

    @_manage_connection
    def getAll(self, _con, cur):
        res = cur.execute("SELECT * FROM sounds ORDER BY name;").fetchall()
        return [self._recordToAudioMetadata(row) for row in res]

    @_manage_connection
    def rename(self, con, cur, old_name, new_name, new_path):
        query = """UPDATE sounds
        SET name = ?, file_path = ?
        WHERE name = ?;"""
        cur.execute(query, (new_name, new_path, old_name))
        con.commit()

    @_manage_connection
    def addTag(self, con, cur, name, tag):
        sound_id = self._getSoundID(name)
        query = "INSERT INTO tags (tag, sound_id) VALUES (?, ?);"
        cur.execute(query, (tag, sound_id))
        con.commit()

    @_manage_connection
    def removeTag(self, con, cur, name, tag):
        sound_id = self._getSoundID(name)
        query = "DELETE FROM tags WHERE sound_id = ? AND tag = ?;"
        cur.execute(query, (sound_id, tag))
        con.commit()

    @_manage_connection
    def _getTags(self, _con, cur, id):
        res = cur.execute("SELECT tag FROM tags WHERE sound_id = ?", (id,))
        return [data[0] for data in res.fetchall()]

    @_manage_connection
    def _getSoundID(self, _con, cur, name):
        return cur.execute("SELECT id FROM sounds WHERE name = ?", (name,)).fetchone()[
            0
        ]

    def _recordToAudioMetadata(self, record):
        tags = self._getTags(record[0])
        return AudioMetadata(
            filePath=record[1],
            name=record[2],
            duration=record[3],
            dateAdded=record[4],
            author=record[5],
            tags=tags,
        )
