import os
import unittest
from src.sqlite_init import create_db
from src.commands import *
from src.sqlite_init import *
from src.sqlite_storage import Sqlite
from src.storage_commander import StorageCommander


class DummyCache:
    def __init__(self):
        pass

    def addSound(self, file_path, name=None, author=None):
        return

    def getByName(self, name):
        return

    def getByTags(self, tags):
        return

    def rename(self, old_name, new_name):
        return

    def addTag(self, name, tag):
        return

    def removeTag(self, name, tag):
        return

    def cache(self, _):
        return


class BasicTests(unittest.TestCase):
    # copy the test_sounds directory so that way we can modify it without worry
    def setUp(self):
        self.db_name = "test/test_audio_archive.db"
        create_db(self.db_name)
        storage = StorageCommander(DummyCache(), Sqlite(self.db_name))
        self.commander = Commander(storage)
        for fname in os.listdir("test/test_sounds"):
            self.commander.addSound(f"test/test_sounds/{fname}")

    def tearDown(self):
        os.remove(self.db_name)

    def test_getSounds(self):
        # sort the sounds so the order is always the same
        sounds = sorted([sound.name for sound in self.commander.getSounds()])
        self.assertListEqual(
            sounds,
            [
                "coffee",
                "coffee-slurp-2",
                "coffee-slurp-3",
                "coffee-slurp-4",
                "coffee-slurp-5",
                "coffee-slurp-6",
                "coffee-slurp-7",
                "coffee-slurp-8",
                "toaster",
                "toaster-2",
            ],
        )

    def test_rename(self):
        self.commander.rename("coffee-slurp-2", "a_new_name")
        names = sorted([sound.name for sound in self.commander.getSounds()])
        self.assertEqual(
            names,
            [
                "a_new_name",
                "coffee",
                "coffee-slurp-3",
                "coffee-slurp-4",
                "coffee-slurp-5",
                "coffee-slurp-6",
                "coffee-slurp-7",
                "coffee-slurp-8",
                "toaster",
                "toaster-2",
            ],
        )


if __name__ == "__main__":
    unittest.main()
