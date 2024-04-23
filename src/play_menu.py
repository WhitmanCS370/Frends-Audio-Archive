from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
import simpleaudio as sa
from threading import Thread
from kivy.config import Config
Config.set('graphics', 'width', '200')
Config.set('graphics', 'height', '150')

class MyGridLayout(GridLayout):
    def __init__ (self, names, commander, options, **kwargs):
        super(MyGridLayout, self).__init__(**kwargs)
        self.cols = 2
        self.paused = True #Stores whether or not the application is paused for the button function
        self.options = options
        self.commander = commander
        self.names = names
        red = [1, 0, 0, 1]  
        green = [0, 1, 0, 1]  
        self.colorOptions = [red, green]

        self.stopRestart = Button(text = "Play",background_color = self.colorOptions[1],
                                  font_size = 32)
        self.stopRestart.bind(on_press = self.stopOrRestartSound)
        self.add_widget(self.stopRestart)
        
    def stopOrRestartSound(self, button):
        if self.paused:
            thread = Thread(target = self.commander.playAudio, args = (self.names, self.options))
            thread.start()
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
        App.__init__(self)# I have to manually call the App Constructor since I overloaded it
        self.commander = commander
        self.options = options
        self.names = names
        
    def build(self):
        return MyGridLayout(self.names, self.commander, self.options)
    
def playMenu(names, commander, options, customThreadClass = None):
    menuApp = PlayMenuApp(names, commander, options)
    if customThreadClass != None:
        customThreadClass.setThreadedValue(menuApp)
    menuApp.run()
    #on window close
    sa.stop_all()
        