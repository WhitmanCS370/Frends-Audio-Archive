from kivy.app import App, Widget
from kivy.uix.label import Label

class BackgroundLabel(Widget):
    pass

class gui_testApp(App):
    def build(self):
        box = BackgroundLabel()
        return box

if __name__ == "__main__":
    gui_testApp().run()