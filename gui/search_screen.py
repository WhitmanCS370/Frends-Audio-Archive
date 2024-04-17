import sys
from kivy.app import App, Widget
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty, StringProperty, NumericProperty

class SearchApp(App):
    def build(self):
        return Search()
    
class Search(Widget):
    query = StringProperty("")

    def search_sound(self):
        print(self.query, file=sys.stdout)

class LabeledCheckbox(BoxLayout):
    text = StringProperty("")
    elemsize = NumericProperty(48)

class Spacer(Widget):
    pass

def main():
    SearchApp().run()


    
if __name__ == "__main__":
    main()