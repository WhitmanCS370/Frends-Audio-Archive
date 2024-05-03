from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.properties import BooleanProperty
from commander import *
from sqlite_storage import Sqlite
from storage_commander import StorageCommander
from kivy.core.window import Window

class HomeScreen(App):
    def __init__(self, commander, GUI_Manager):
        App.__init__(self)
        self.GUI_Manager = GUI_Manager
        self.commander = commander
    button_clicked = BooleanProperty(False)

    def build(self):
        self.set_window_size_to_full_screen()
        buttons = BoxLayout(orientation="horizontal")
        file_input = TextInput(text="Enter path to sound", multiline=False)
        file_input.bind(on_text_validate=self.on_enter)
        play = Button(text="Play sounds")
        play.bind(on_release=self.on_button_click)
        buttons.add_widget(file_input)
        buttons.add_widget(play)
        return buttons
    
    def closeWindow(self):
        self.GUI_Manager.toggleTokenOff()
        App.get_running_app().stop() 

    def on_button_click(self, instance):
        self.button_clicked = True
        self.closeWindow()

    def on_enter(self, value):
        storage = self.commander.fetchStorageCommander()
        storage.addSound(value.text)
    
    def set_window_size_to_full_screen(self):
        Window.fullscreen = 'auto'
