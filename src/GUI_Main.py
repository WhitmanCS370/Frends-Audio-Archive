from play_menu import playMenu
from threading import Thread
from sqlite_init import create_db
from home_screen import HomeScreen
from commander import Commander
from search_screen_new import SearchPageApp
from effectPopUp import Settings
from pathlib import Path
from playback_options import PlaybackOptions
import os
import os.path


# create the database if it doesn't exit, otherwise pass
def checkForPriorSetUp():
    path = "audio_archive.db"
    check_file = os.path.isfile(path)
    if not check_file:
        create_db()


class GUI_Manager:

    def __init__(self):
        # setup
        checkForPriorSetUp()
        self.base_dir = Path("sounds")
        self.commander = Commander(sounds_directory="../sounds")
        self.listOfSounds = None
        self.options = None
        self.token = False

    # method so that called GUIs can tell the manager to continue to
    # function after closing
    def toggleTokenOff(self):
        self.token = False

    # setter function to set sound list for the search GUI
    def setSoundList(self, list):
        self.listOfSounds = list

    # setter function to set the options object for the options pop-up GUI given Rhys's effectData object
    def setSoundOptions(self, effectData):
        effectDict = effectData.get_values()
        self.options = PlaybackOptions(
            speed=effectDict["speed"],
            volume=effectDict["volume"],
            reverse=effectDict["reverse"],
            start_percent=(effectDict["crop_percent"][0]) / 100,
            end_percent=(effectDict["crop_percent"][1]) / 100,
            start_sec=None,
            end_sec=None,
            save=None,  # same as below comment
            transpose=effectDict["transpose"],
            parallel=None,
        )

    # shouldStopMenu is like a token, and determines whether the program exits prematurely
    # the called GUI has the responisbility of setting the token to False on exit, as if it doesn't,
    # the program assumes that the menu was forcibly closed and shouldn't continue
    def runMenuCycle(self):
        while True:
            # start home screen, nothing gets returned
            if not self.token:
                self.token = True
                mainMenu = HomeScreen(self.commander, self)
                mainMenu.run()
            if not self.token:
                self.token = True
                print("searchMenuOpened")
                searchScreen = SearchPageApp(self.commander, self)
                searchScreen.run()
                # test that the  GUI_Manager was correctly passed the sound list
                print("sounds passed:")
                for sound in self.listOfSounds:
                    print(sound)
            if not self.token:
                self.token = True
                print("settingsMenuOpened")
                settingsScreen = Settings(self.commander, self)
                settingsScreen.run()
            if not self.token:
                print("playedSounds")
                playMenu(self.listOfSounds, self.commander, self.options)
                # runPlayMenu
                # loopBackToTop
            if self.token:
                break
        return


def main():
    manager = GUI_Manager()
    manager.runMenuCycle()
    print("Thanks for using our audio archive!!!")


if __name__ == "__main__":
    main()
