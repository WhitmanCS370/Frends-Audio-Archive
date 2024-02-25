from pathlib import Path
import sqlite3
import time


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
    def add_sound(self, con, cur, file_path, name=None, author=None):
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError()
        if name is None:
            # convert file_path to name of file without extension
            name = path.stem
        duration = 10
        cur_time = int(time.time())
        query = """INSERT INTO sounds (file_path, name, duration, date_added, last_accessed, author)
        VALUES (?, ?, ?, ?, ?, ?);"""
        cur.execute(query, (file_path, name, duration, cur_time, cur_time, author))
        con.commit()

    @_manage_connection
    def get(self, _con, cur, name):
        res = cur.execute("SELECT * FROM sounds WHERE name = ?;", (name,))
        data = res.fetchone()
        return AudioObject(data[0], data[1], data[2])

    @_manage_connection
    def get_all(self, _con, cur):
        res = None
        if cur is not None:
            res = cur.execute("SELECT * FROM sounds ORDER BY name;").fetchall()
        else:
            raise Exception("Cursor is None")
        return res

    @_manage_connection
    def rename(self, con, cur, old_name, new_name):
        query = """UPDATE sounds
        SET name = ?
        WHERE name = ?;"""
        cur.execute(query, (new_name, old_name))
        con.commit()
