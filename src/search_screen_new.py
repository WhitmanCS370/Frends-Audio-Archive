from kivy.uix.boxlayout import BoxLayout
from kivy.app import App, Widget
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from storage_commander import StorageCommander

class SearchBoxLayout(BoxLayout):
    query = ''
    def __init__(self, commander):
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
        print(self.commander.fuzzySearch(self.query, n=5), flush=True)
        print("name?: ", self.boxes.name, flush=True)
        print("Tag?: ", self.boxes.tag, flush=True)

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



class SearchScreenApp(App):
    def build(self):
        return SearchBoxLayout()
    
if __name__ == "__main__":
    storage = StorageCommander(Sqlite())
    commander = Commander(storage)
    SearchScreenApp(commander).run()