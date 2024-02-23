import shutil
import unittest
from src.commands import *


class BasicTests(unittest.TestCase):
    # copy the test_sounds directory so that way we can modify it without worry
    def setUp(self):
        self.commander = Commander()
        self.dir = "test/test_sounds_copy/"
        shutil.copytree("test/test_sounds", self.dir)

    def tearDown(self):
        shutil.rmtree(self.dir)

    def test_getSounds(self):
        # sort the sounds so the order is always the same
        sounds = sorted(self.commander.getSounds(self.dir))
        self.assertListEqual(
            sounds,
            [
                "coffee-slurp-2.wav",
                "coffee-slurp-3.wav",
                "coffee-slurp-4.wav",
                "coffee-slurp-5.wav",
                "coffee-slurp-6.wav",
                "coffee-slurp-7.wav",
                "coffee-slurp-8.wav",
                "coffee.wav",
                "toaster-2.wav",
                "toaster.wav",
            ],
        )

    def test_rename(self):
        # new_sound should have ".wav" appended to it
        self.commander.rename(f"{self.dir}coffee-slurp-2.wav", f"{self.dir}new_sound")
        self.commander.rename(f"{self.dir}coffee-slurp-3.wav", f"{self.dir}other_sound.wav")
        sounds = sorted(self.commander.getSounds(self.dir))
        self.assertListEqual(
            sounds,
            [
                "coffee-slurp-4.wav",
                "coffee-slurp-5.wav",
                "coffee-slurp-6.wav",
                "coffee-slurp-7.wav",
                "coffee-slurp-8.wav",
                "coffee.wav",
                "new_sound.wav",
                "other_sound.wav",
                "toaster-2.wav",
                "toaster.wav",
            ],
        )


if __name__ == "__main__":
    unittest.main()
