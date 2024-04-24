# chat gpt helped me make this https://chat.openai.com/share/6e4052cc-d1ea-4722-b5dc-d63b152576ce
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout


class SoundManager(App):
    def build(self):
        layout = BoxLayout(orientation="horizontal", spacing=10, padding=10)

        add_sounds_button = Button(text="Add Sounds")
        add_sounds_button.bind(on_press=self.add_sounds)

        play_sounds_button = Button(text="Play Sounds")
        play_sounds_button.bind(on_press=self.play_sounds)

        show_sounds_button = Button(text="Show Sounds")
        show_sounds_button.bind(on_press=self.show_sounds)

        layout.add_widget(add_sounds_button)
        layout.add_widget(play_sounds_button)
        layout.add_widget(show_sounds_button)

        return layout

    def add_sounds(self, instance):
        print("Add Sounds button clicked")

    def play_sounds(self, instance):
        print("Play Sounds button clicked")

    def show_sounds(self, instance):
        print("Show Sounds button clicked")


if __name__ == "__main__":
    SoundManager().run()
