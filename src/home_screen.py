from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from commands import *
from sqlite_storage import Sqlite
from storage_commander import StorageCommander

commander = Commander(StorageCommander(Sqlite()))


def on_enter(value):
    commander.addSound(value.text)


class HomeScreen(App):
    def build(self):
        buttons = BoxLayout(orientation="horizontal")
        file_input = TextInput(text="Enter path to sound", multiline=False)
        file_input.bind(on_text_validate=on_enter)
        play = Button(text="Play sounds")
        buttons.add_widget(file_input)
        buttons.add_widget(play)
        return buttons


if __name__ == "__main__":
    HomeScreen().run()
