import os
from pathlib import Path
import shutil
import unittest
from src.sqlite_init import create_db
from src.commands import *
from src.dummy_cache import DummyCache
from src.sqlite_init import *
from src.sqlite_storage import Sqlite
from src.storage_commander import StorageCommander


def addAllSounds(base_dir, commander):
    for fname in os.listdir(base_dir):
        commander.addSound(os.path.join(base_dir, fname))


class BasicTests(unittest.TestCase):
    # copy the test_sounds directory so that way we can modify it without worry
    def setUp(self):
        self.base_dir = os.path.join("test", "temp_test_sounds")
        shutil.copytree(os.path.join("test", "test_sounds"), self.base_dir)
        self.db_name = os.path.join("test", "test_audio_archive.db")
        create_db(self.db_name)
        storage = StorageCommander(DummyCache(), Sqlite(self.db_name), self.base_dir)
        self.commander = Commander(storage)

    def tearDown(self):
        os.remove(self.db_name)
        shutil.rmtree(self.base_dir)

    def test_addSoundInDirSameName(self):
        self.commander.addSound(os.path.join(self.base_dir, "coffee.wav"))
        sound = self.commander.storage.getByName("coffee")
        # the new sound should be in the database
        self.assertEqual(sound.name, "coffee")
        self.assertTrue(os.path.exists(sound.file_path))

    def test_addSoundInDirNewName(self):
        self.commander.addSound(os.path.join(self.base_dir, "coffee.wav"), "new_sound")
        sound = self.commander.storage.getByName("new_sound")
        # the new sound should be in the database
        self.assertEqual(sound.name, "new_sound")
        # the file should be renamed
        self.assertTrue(os.path.exists(os.path.join(self.base_dir, "new_sound.wav")))
        # the old file should not be there
        self.assertFalse(os.path.exists(os.path.join(self.base_dir, "coffee.wav")))

    def test_addSoundOtherDirSameName(self):
        old_path = os.path.join("test_sound.wav")
        shutil.move(os.path.join(self.base_dir, "coffee.wav"), old_path)
        self.commander.addSound(old_path)
        sound = self.commander.storage.getByName("test_sound")
        # the new sound should be in the database
        self.assertEqual(sound.name, "test_sound")
        # the file should be renamed
        self.assertTrue(os.path.exists(os.path.join(self.base_dir, "test_sound.wav")))
        # the old file should be there too
        self.assertTrue(os.path.exists(old_path))
        os.remove(old_path)

    def test_addSoundOtherDirNewName(self):
        old_path = os.path.join("test_sound.wav")
        shutil.move(os.path.join(self.base_dir, "coffee.wav"), old_path)
        self.commander.addSound(old_path, "new_sound")
        sound = self.commander.storage.getByName("new_sound")
        # the new sound should be in the database
        self.assertEqual(sound.name, "new_sound")
        # the file should be renamed
        self.assertTrue(os.path.exists(os.path.join(self.base_dir, "new_sound.wav")))
        # the old file should be there too
        self.assertTrue(os.path.exists(old_path))
        os.remove(old_path)

    def test_addSoundAlreadyExists(self):
        path = os.path.join(self.base_dir, "coffee.wav")
        # we should be able to add this the first time but not the second
        self.assertTrue(self.commander.addSound(path))
        self.assertFalse(self.commander.addSound(path))

    def test_removeSoundSuccess(self):
        path = os.path.join(self.base_dir, "coffee.wav")
        self.commander.addSound(path)
        self.assertTrue(self.commander.removeSound("coffee"))
        self.assertFalse(os.path.exists(path))

    def test_removeSoundFail(self):
        # can't remove a sound if it doesn't exist
        self.assertFalse(self.commander.removeSound("coffee"))

    def test_addTag(self):
        addAllSounds(self.base_dir, self.commander)
        self.commander.addTag("coffee", "example tag")
        self.commander.addTag("coffee-slurp-2", "example tag")
        audios = self.commander.storage.getByTags(["example tag"])
        names = {audio.name for audio in audios}
        self.assertSetEqual(names, {"coffee", "coffee-slurp-2"})

    def test_removeTag(self):
        addAllSounds(self.base_dir, self.commander)
        self.commander.addTag("coffee", "example tag")
        self.commander.removeTag("coffee", "example tag")
        audios = self.commander.storage.getByTags("example tag")
        self.assertEqual(len(audios), 0)

    def test_renameSuccess(self):
        addAllSounds(self.base_dir, self.commander)
        self.assertTrue(self.commander.rename("coffee", "new_name"))
        sound = self.commander.storage.getByName("new_name")
        self.assertEqual(Path(sound.file_path).stem, "new_name")
        self.assertEqual(sound.name, "new_name")
        self.assertTrue(os.path.exists(os.path.join(self.base_dir, "new_name.wav")))
        self.assertFalse(os.path.exists(os.path.join(self.base_dir, "coffee.wav")))

    def test_renameBadOldName(self):
        addAllSounds(self.base_dir, self.commander)
        self.assertFalse(self.commander.rename("this_isn't_a_name", "new_name"))

    def test_renameBadNewName(self):
        addAllSounds(self.base_dir, self.commander)
        self.assertFalse(self.commander.rename("coffee", "coffee-slurp-2"))

    def test_getSounds(self):
        addAllSounds(self.base_dir, self.commander)
        sounds = {sound.name for sound in self.commander.getSounds()}
        self.assertSetEqual(
            sounds,
            {
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
            },
        )


if __name__ == "__main__":
    unittest.main()
