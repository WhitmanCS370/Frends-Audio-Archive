from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from storage_commander import StorageCommander
from sqlite_storage import Sqlite
from commander import Commander
from kivy.core.window import Window


class SearchScreenLayout(BoxLayout):
    query = ""

    def __init__(self, commander, GUI_Manager):
        super().__init__(orientation="vertical", padding=50, spacing=10)
        self.commander = commander
        self.GUI_Manager = GUI_Manager
        self.add_widget(Label(text="Frends Search", font_size=50))
        self.searchbox = TextInput(
            hint_text="search here",
            size=(self.width / 2.0, 10),
            font_size=60,
            base_direction="ltr",
            halign="center",
            multiline=False,
        )
        self.searchbox.bind(text=self.update_query)
        self.add_widget(self.searchbox)

        self.boxes = CheckboxesLayout()
        self.add_widget(self.boxes)

        self.search_button = Button(text="Search")
        self.search_button.bind(on_press=self.search_sound)
        self.add_widget(self.search_button)

    def update_query(self, instance, value):
        self.query = value

    def search_sound(self, instance):
        storage = self.commander.fetchStorageCommander()
        res = storage.fuzzySearch(self.query, n=5)
        popup = Popup(title="Search Results", size_hint=(None, None), size=(1200, 800))
        search_results = SearchResults(results=res, popup_instance=popup)
        popup.content = search_results
        popup.open()

        def submit_results(
            instance,
        ):  # also functions to pass the token back to the GUI manager!
            selected_sounds = search_results.selected_sounds
            self.GUI_Manager.setSoundList(selected_sounds)
            self.GUI_Manager.toggleTokenOff()
            print("Selected sounds:")
            for sound in selected_sounds:
                print(sound)
            popup.dismiss()
            App.get_running_app().stop()

        search_results.submit_button.bind(on_press=submit_results)


class CheckboxesLayout(BoxLayout):
    name = True
    tag = True

    def __init__(self):
        super().__init__(orientation="horizontal", padding=20)
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
    def __init__(self, results, popup_instance, **kwargs):
        super(SearchResults, self).__init__(
            **kwargs, orientation="vertical", padding=20, spacing=20
        )
        self.results = results
        self.selected_sounds = []

        for result in results:
            # print(result)
            box = MetadataDisplay(
                result, name=result.name, on_checkbox_active=self.checkbox_active
            )
            self.add_widget(box)

        self.submit_button = Button(text="Submit")
        self.submit_button.bind(on_press=lambda instance: self.submit(popup_instance))
        self.add_widget(self.submit_button)

    def checkbox_active(self, checkbox_instance, value, sound_name):
        print(f"Checkbox '{sound_name}' activated: {value}")
        if value:
            self.selected_sounds.append(sound_name)
        else:
            self.selected_sounds.remove(sound_name)

    def submit(self, popup_instance):
        print("Submit function called")
        print("Selected sounds:")
        for sound in self.selected_sounds:
            print(sound)
        popup_instance.dismiss()  # Close the parent Popup


class MetadataDisplay(BoxLayout):
    def __init__(self, dataList, name, on_checkbox_active, **kwargs):
        super(MetadataDisplay, self).__init__(**kwargs, orientation="horizontal")

        self.name = name

        self.checkbox = CheckBox()
        self.checkbox.bind(
            active=lambda instance, value: on_checkbox_active(
                instance, value, self.name
            )
        )
        self.add_widget(self.checkbox)

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


class SearchPageApp(App):
    def __init__(self, commander, GUI_Manager):
        self.commander = commander
        self.GUI_Manager = GUI_Manager
        App.__init__(self)

    def closeWindow(self):
        self.GUI_Manager.toggleTokenOff()
        App.get_running_app().stop()

    def on_key_down(
        self, *args
    ):  # Adjusted method signature to accept any number of arguments
        keyboard, keycode, text, modifiers = args[:4]
        # Check if the pressed key is the escape key (keycode 27)
        if keycode == 27:
            self.GUI_Manager.setSoundList([])
            print("Thanks for using our audio archive!!!")
            import sys

            sys.exit()

    def build(self):
        Window.bind(on_key_down=self.on_key_down)
        return SearchScreenLayout(self.commander, self.GUI_Manager)
