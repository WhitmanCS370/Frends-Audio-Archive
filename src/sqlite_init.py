"""
This module is in charge of initializing the sqlite database to store information about
sounds in the audio archive.  It should only need to be called once.
Design notes: I chose to make the file_path field a VARCHAR(260) because the maximum
path length is 260 on Windows.
See https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=registry
"""

import sqlite3


def create_db(db_name="audio_archive.db"):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    create_sounds_table_query = """CREATE TABLE IF NOT EXISTS sounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path VARCHAR(260) NOT NULL UNIQUE,
            name VARCHAR(128) NOT NULL UNIQUE,
            duration INTEGER NOT NULL,
            date_added INTEGER NOT NULL,
            last_accessed INTEGER NOT NULL,
            author VARCHAR(128)
            );"""

    create_tags_table_query = """CREATE TABLE IF NOT EXISTS tags (
            tag VARCHAR(128) NOT NULL,
            sound_id NOT NULL,
            PRIMARY KEY (tag, sound_id),
            FOREIGN KEY (sound_id)
            REFERENCES sounds (sound_id)
                ON DELETE CASCADE
            );"""
    cur.execute(create_sounds_table_query)
    cur.execute(create_tags_table_query)
    con.close()


if __name__ == "__main__":
    create_db()
