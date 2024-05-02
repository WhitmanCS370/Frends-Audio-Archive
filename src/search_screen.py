import sys
from kivy.app import App, Widget
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from commands import Commander
from storage_commander import StorageCommander
from sqlite_storage import Sqlite

storage = StorageCommander(Sqlite())
commander = Commander(storage)

class SearchApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(Search(name='searchbox'))
        sm.add_widget(SearchResultScreen(name='searchresultscreen'))
        sm.current = 'searchbox'
        return sm
    
class Search(Screen):
    query = StringProperty("")

    def search_sound(self):
        result = commander.fuzzySearch(str(Search.query), n=1)[0]
        

class SearchResultScreen(Screen):
    self.add_widget(Widget)

        
class SearchResult(Widget):
    metadata = ObjectProperty(None)

    



class LabeledCheckbox(BoxLayout):
    text = StringProperty("")
    is_active = BooleanProperty(True)
    elemsize = NumericProperty(48)

class SearchResult(Screen):
    pass

class Spacer(Widget):
    pass

def main():
    SearchApp().run()


    
if __name__ == "__main__":
    main()
    