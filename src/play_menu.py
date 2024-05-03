from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
import simpleaudio as sa
from threading import Thread
from kivy.config import Config
from kivy.core.window import Window

Config.set("graphics", "width", "200")
Config.set("graphics", "height", "150")


class MyGridLayout(GridLayout):
    def __init__(self, names, commander, options, **kwargs):
        super(MyGridLayout, self).__init__(**kwargs)
        self.cols = 2
        self.paused = True  # Stores whether or not the application is paused for the button function
        self.options = options
        self.commander = commander
        self.names = names
        self.thread = None
        red = [1, 0, 0, 1]
        green = [0, 1, 0, 1]
        self.colorOptions = [red, green]

        self.stopRestart = Button(
            text="Play", background_color=self.colorOptions[1], font_size=32
        )
        self.stopRestart.bind(on_press=self.stopOrRestartSound)
        self.add_widget(self.stopRestart)

        self.menuButton = Button(text="Quit to Menu", font_size=32)
        self.menuButton.bind(on_press=self.quitToMenu)
        self.add_widget(self.menuButton)

    def quitToMenu(self, button):
        App.get_running_app().stop()

    def stopOrRestartSound(self, button):
        if self.paused:
            self.thread = Thread(
                target=self.commander.playAudio, args=(self.names, self.options)
            )
            self.thread.start()
            self.stopRestart.text = "Stop"
            self.stopRestart.background_color = self.colorOptions[0]
        else:
            self.stopRestart.text = "Play"
            self.stopRestart.background_color = self.colorOptions[1]
            sa.stop_all()
        self.paused = not self.paused
        return None


class PlayMenuApp(App):
    def __init__(self, names, commander, options):
        App.__init__(
            self
        )  # I have to manually call the App Constructor since I overloaded it
        self.commander = commander
        self.options = options
        self.names = names

    def on_key_down(
        self, *args
    ):  # Adjusted method signature to accept any number of arguments
        keyboard, keycode, text, modifiers = args[:4]
        # Check if the pressed key is the escape key (keycode 27)
        if keycode == 27:
            sa.stop_all()

    def build(self):
        Window.bind(on_key_down=self.on_key_down)
        return MyGridLayout(self.names, self.commander, self.options)


def playMenu(names, commander, options, customThreadClass=None):
    menuApp = PlayMenuApp(names, commander, options)
    if customThreadClass != None:
        customThreadClass.setThreadedValue(menuApp)
    menuApp.run()
    # on window close
    sa.stop_all()
