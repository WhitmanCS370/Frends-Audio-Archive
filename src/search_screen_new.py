from kivy.uix.boxlayout import BoxLayout
from kivy.app import App, Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from storage_commander import StorageCommander
from sqlite_storage import Sqlite
from commands import Commander

class SearchScreenLayout(BoxLayout):
    query = ''
    def __init__(self):
        super().__init__(orientation='vertical', padding=50, spacing=10)
        self.commander = commander
        self.add_widget(Label(text="Johns Frends Search", font_size=50))
        searchbox = TextInput(  \
            hint_text='search here',\
            size=(self.width / 2., 10), \
            font_size=60,           \
            base_direction='ltr',   \
            halign='center',        \
            multiline=False
            )
        searchbox.bind(text=self.update_query)
        self.add_widget(searchbox)
        self.boxes = CheckboxesLayout()
        self.add_widget(self.boxes)
        searchbutton = Button(text='Search')
        searchbutton.bind(on_press=self.search_sound)
        self.add_widget(searchbutton)
    
    def update_query(self, instance, value):
        self.query = value

    def search_sound(self, instance):
        res = self.commander.fuzzySearch(self.query, n=5)
        popup = Popup(title='test popup', content=SearchResults(res))
        popup.open()
        
class CheckboxesLayout(BoxLayout):
    name = True
    tag = True
    def __init__(self):
        super().__init__(orientation='horizontal', padding=20)
        namebox = CheckBox(active=self.name)
        namebox.bind(active=self.name_active)
        self.add_widget(namebox)
        self.add_widget(Label(text="Name"))
        tagbox = CheckBox(active=self.tag)
        tagbox.bind(active=self.tag_active)
        self.add_widget(tagbox)
        self.add_widget(Label(text="Tag"))
    
    def name_active(self, checkbox_instance, value):
        self.name = value
    
    def tag_active(self, checkbox_instance, value):
        self.tag = value
        

class SearchResults(BoxLayout):
    def __init__(self, results, **kwargs):
        super(SearchResults, self).__init__(**kwargs, orientation='vertical', padding=20, spacing=20)


        for result in results:
            box = MetadataDisplay(result, name=result.name)
            self.add_widget(box)

class MetadataDisplay(BoxLayout):
    def __init__(self, dataList, name, **kwargs):
        super(MetadataDisplay, self).__init__(**kwargs, orientation='vertical')
        
        self.name = name
        with self.canvas:
            # Set border color
            Color(118, 120, 140, 0.2)
            # Draw border
            self.border = Rectangle(pos=self.pos, size=self.size)
        
        # Bind the update_border method to the size and pos properties
        self.bind(pos=self.update_border, size=self.update_border)
        
        # Iterate over the object's elements and add them to the layout
        soundName = Label(text=f"Name: {dataList.name}")
        soundAuthor = Label(text=f"Author: {dataList.author}")
        soundDuration = Label(text=f"Duration: {dataList.duration}")
        
        self.add_widget(soundName)
        self.add_widget(soundAuthor)
        self.add_widget(soundDuration)
    
    def update_border(self, *args):
        # Update border size and position when widget size or position changes
        self.border.pos = self.pos
        self.border.size = self.size

# class SearchScreen(Screen):
#     def __init__(self, **kwargs):
#         super(SearchScreen, self).__init__(**kwargs)

#         searchScreen = SearchScreenLayout()
#         self.add_widget(searchScreen)


# class ResultsScreen(Screen):
#     def __init__(self, results **kwargs):
#         super(ResultsScreen, self).__init__(**kwargs)

#         resultslist = SearchResults(results)

class SearchPageApp(App):
    def build(self):
        return SearchScreenLayout()
    
if __name__ == "__main__":
    storage = StorageCommander(Sqlite())
    commander = Commander(storage)
    SearchPageApp().run()