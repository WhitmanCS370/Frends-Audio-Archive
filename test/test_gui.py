from pathlib import Path
import shutil
from src.sqlite_init import create_db
from src.commander import *
from src.constants import *
from src.sqlite_init import *
from src.play_menu import playMenu
from src.playback_options import PlaybackOptions
import time
from threading import Thread


def addAllSounds(base_dir, commander):
    for path in Path(base_dir).iterdir():
        commander.addSound(path)


class customThread:

    def __init__(self):
        self.value = None

    def setThreadedValue(self, value):
        self.value = value

    def getThreadedValue(self):
        return self.value


class Test_GUI:

    # setup database and commander w/ default sound options
    def __init__(self):
        self.base_dir = Path("test", "temp_test_sounds")
        shutil.copytree(Path("test", "test_sounds"), self.base_dir)
        self.db_name = Path("test", "test_audio_archive.db")
        create_db(str(self.db_name))
        self.commander = Commander(str(self.base_dir), str(self.db_name))
        addAllSounds(self.base_dir, self.commander)
        self.defaultOptions = PlaybackOptions(
            speed=None,
            volume=None,
            reverse=None,
            start_percent=None,
            end_percent=None,
            start_sec=None,
            end_sec=None,
            save=None,
            transpose=None,
            parallel=None,
        )

    # remove directories
    def stopTesting(self):
        Path(self.db_name).unlink()
        shutil.rmtree(self.base_dir)

    # Threaded instance of the play menu will show up, can progress to the next
    # test on window close
    def testPlayMenu(self, soundsToPlay):
        sounds = self.commander.getSounds()
        print("printing names...")
        for sound in sounds:
            print(sound)
        custom = customThread()
        thread = Thread(
            target=playMenu,
            args=(soundsToPlay, self.commander, self.defaultOptions, custom),
        )
        thread.start()
        time.sleep(3)
        thread.join()
        app = custom.getThreadedValue()
        app.stop()
        self.stopTesting()


if __name__ == "__main__":
    tester = Test_GUI()
    tester.testPlayMenu(["coffee", "coffee-slurp-6", "toaster", "coffee-slurp-2"])
    # more tests could go here, they should play one at a time, progressing on tab close
    print("goodbye")
