"""
This module is in charge of initializing the sqlite database to store information about
sounds in the audio archive.  It should only need to be called once.
Design notes: I chose to make the file_path field a VARCHAR(260) because the maximum
path length is 260 on Windows.
See https://learn.microsoft.com/en-us/windows/win32/fileio/maximum-file-path-limitation?tabs=registry
"""

import sqlite3

from constants import *


def create_db(db_name="audio_archive.db"):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    # Note: sqlite automatically creates an index for UNIQUE columns so we don't need
    # to create an index for name.
    # See https://stackoverflow.com/questions/36879755/no-need-to-create-an-index-on-a-column-with-a-unique-constraint-right
    # Note: The sqlite3 module would not allow me to use a placeholder value for setting
    # the VARCHAR length. However, I don't think that using a constant like this creates
    # any vulnerabilities, so a f-string should be fine.
    create_sounds_table_query = f"""CREATE TABLE IF NOT EXISTS sounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path VARCHAR(260) NOT NULL UNIQUE,
            name VARCHAR({MAX_SOUND_NAME_LENGTH}) NOT NULL UNIQUE,
            duration INTEGER NOT NULL,
            date_added INTEGER NOT NULL,
            last_played INTEGER,
            author VARCHAR({MAX_AUTHOR_LENGTH})
            );"""

    create_tags_table_query = f"""CREATE TABLE IF NOT EXISTS tags (
            tag VARCHAR({MAX_TAG_LENGTH}) NOT NULL,
            sound_id NOT NULL,
            PRIMARY KEY (tag, sound_id),
            FOREIGN KEY (sound_id) REFERENCES sounds (id)
                ON DELETE CASCADE
            );"""
    cur.execute(create_sounds_table_query)
    cur.execute(create_tags_table_query)
    con.close()


if __name__ == "__main__":
    create_db()
