import os
import unittest
from src.sqlite_init import *
from src.sqlite_storage import *
from src.commands import *


class BasicTests(unittest.TestCase):
    # copy the test_sounds directory so that way we can modify it without worry
    def setUp(self):
        self.db_name = "test/test_audio_archive.db"
        create_db(self.db_name)
        storage = Sqlite(self.db_name)
        self.commander = Commander(storage)
        for fname in os.listdir("test/test_sounds"):
            storage.add_sound(f"test/test_sounds/{fname}")

    def tearDown(self):
        os.remove(self.db_name)
        # shutil.rmtree(self.db_name)

    def test_getSounds(self):
        # sort the sounds so the order is always the same
        sounds = sorted([sound[1] for sound in self.commander.getSounds()])
        self.assertListEqual(
            sounds,
            [
                "test/test_sounds/coffee-slurp-2.wav",
                "test/test_sounds/coffee-slurp-3.wav",
                "test/test_sounds/coffee-slurp-4.wav",
                "test/test_sounds/coffee-slurp-5.wav",
                "test/test_sounds/coffee-slurp-6.wav",
                "test/test_sounds/coffee-slurp-7.wav",
                "test/test_sounds/coffee-slurp-8.wav",
                "test/test_sounds/coffee.wav",
                "test/test_sounds/toaster-2.wav",
                "test/test_sounds/toaster.wav",
            ],
        )

    def test_rename(self):
        self.commander.rename("coffee-slurp-2", "a_new_name")
        names = sorted([sound[2] for sound in self.commander.getSounds()])
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
