from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.relativelayout import RelativeLayout
from kivy.core.window import Window

EFFECT_DATA = None
"""
Popup that allows the user to change the values of the effects

The effects are stored in a dictionary in the Singleton EffectData class
Determines the type of input to create based on the data type of the effect using "effect_map"

"""
class effectsPopUp(Popup):
    def __init__(self, main_window, **kwargs):
        global EFFECT_DATA
        super(effectsPopUp, self).__init__(**kwargs)
        effect_map = {bool: CheckBoxInput, float: SliderInput, int: SliderInput, list: DoubleRangeSliderInput}
        self.title = 'Effects'
        self.layout = BoxLayout(orientation='vertical')
        self.inputs = []
        self.main_window = main_window
        
        # Create an input for each effect
        for name, type in EFFECT_DATA.get_types().items():
            _val = EFFECT_DATA.get_values()[name]
            _min = EFFECT_DATA.get_mins()[name]
            _max = EFFECT_DATA.get_maxs()[name]
            new_input = effect_map[type](name, _val, type, _min, _max)    
            self.layout.add_widget(new_input.get_layout())
            self.inputs.append(new_input)
        
        # Create a close button that updates the main window before closing the popup using pre_dismiss
        close_button = Button(text='Close', size_hint=(1, None), height=40)
        close_button.bind(on_press=self.pre_dismiss)
        
        self.layout.add_widget(close_button)
        self.content = self.layout
    
    def pre_dismiss(self, instance):
        self.update_main_window()
        super().dismiss()

    def update_main_window(self):
        global EFFECT_DATA
        for obj in self.inputs:
            EFFECT_DATA.assign_value(obj.get_name(), obj.get_value())
        self.main_window.update_value_label()
        
"""
Contains:
    - The name of the effect as a Label
    - A checkbox input for boolean values
"""
class CheckBoxInput():
    def __init__(self, name, current, type, min, max):
        self.name = name
        self.sub_layout = BoxLayout(orientation='horizontal')
        self.checkbox = CheckBox(active=current)
        self.name_label = Label(text=self.name)
        self.sub_layout.add_widget(self.name_label)
        self.sub_layout.add_widget(self.checkbox)
    
    def get_name(self):
        return self.name

    def get_layout(self):
        return self.sub_layout
    
    def get_value(self):
        return self.checkbox.active

"""
Contains:
    - The name of the effect as a Label
    - A slider input for int or float values
    - A current value label above the slider, moves with the slider
"""
class SliderInput():
    def __init__(self, name, current, type, min, max):
        self.name = name
        self.type = type
        self.min = min
        self.max = max
        self.sub_layout = BoxLayout(orientation='horizontal')
        self.value_layout = BoxLayout(orientation='vertical')
        self.slider = Slider(min=min, max=max, value=current, size_hint=(1, 2), height=40)
        self.name_label = Label(text=self.name)
        
        # Create a RelativeLayout to position the value label above the slider
        self.relative_layout = RelativeLayout()
        self.value_label = Label(text=str(round(self.type(current), 2)), size_hint=(None, None), size=(100, 40), pos_hint={'center_x': 0.5, 'top': 0.85}) 
        self.relative_layout.add_widget(self.value_label)
        self.value_layout.add_widget(self.relative_layout)
        self.value_layout.add_widget(self.slider)

        self.slider.bind(value=self.update_value)

        self.sub_layout.add_widget(self.name_label)
        self.sub_layout.add_widget(self.value_layout)
    
    def update_value(self, instance, value):
        self.value_label.text = str(round(self.type(value), 2))
        self.value_label.pos_hint = {'center_x': ((instance.value - self.min) / (self.max - self.min))}
    
    def get_name(self):
        return self.name
    
    def get_layout(self):
        return self.sub_layout
    
    def get_value(self):
        return self.slider.value

"""
Contains:
    - The name of the effect as a Label
    - Two slider inputs for a range of values
    - A current value label above the sliders, does not move with the sliders

The sliders are bound to each other to prevent the min slider from being greater than the max slider

"""
class DoubleRangeSliderInput():
    def __init__(self, name, current, type, min, max):
        self.name = name
        self.type = type
        self.min = min
        self.max = max
        self.sub_layout = BoxLayout(orientation='horizontal')
        self.value_layout = BoxLayout(orientation='vertical')
        self.name_label = Label(text=self.name)
        
        self.range_label = Label(text=f"{current[0]}-{current[1]}%")
        self.value_layout.add_widget(self.range_label)
        
        self.slider_min = Slider(min=min, max=max, value=current[0])
        self.slider_min.bind(value=self.update_max_slider)
        self.value_layout.add_widget(self.slider_min)
        
        self.slider_max = Slider(min=min, max=max, value=current[1])
        self.slider_max.bind(value=self.update_min_slider)
        self.value_layout.add_widget(self.slider_max)

        self.sub_layout.add_widget(self.name_label)
        self.sub_layout.add_widget(self.value_layout)
    
    def update_max_slider(self, instance, value):
        # does not push the slider to past max
        if value >= self.max:
            return
        self.update_range_label()
        # does not allow the max slider to be greater than the min slider
        if value >= self.slider_max.value:
            self.slider_max.value = value + 1

    def update_min_slider(self, instance, value):
        # does not push the slider to past min
        if value <= self.min+1:
            return
        self.update_range_label()
        # does not allow the min slider to be greater than the max slider
        if value <= self.slider_min.value:
            self.slider_min.value = value - 1
    
    def update_range_label(self):
        self.range_label.text = f"{int(self.slider_min.value)}-{int(self.slider_max.value)}%"
    
    def get_name(self):
        return self.name
    
    def get_layout(self):
        return self.sub_layout
    
    def get_value(self):
        return (int(self.slider_min.value), int(self.slider_max.value))
    
"""
Temporary main window to display the values of the effects (EFFECT_DATA) and a buttom to open the popup

"""
class MainWindow(BoxLayout):
    def __init__(self, commander, GUI_Manager, **kwargs):
        super(MainWindow, self).__init__(**kwargs)
        global EFFECT_DATA
        self.commander = commander
        self.GUI_Manager = GUI_Manager
        self.values = EFFECT_DATA.get_values()
        self.orientation = 'vertical'
        self.value_label = Label(text=self.dict_to_str(self.values))
        self.add_widget(self.value_label)
        self.button = Button(text="Open Popup")
        self.button.bind(on_press=self.open_popup)
        self.add_widget(self.button)
        self.playButton = Button(text="Play")
        self.playButton.bind(on_press=self.play_sound)
        self.add_widget(self.playButton)

    def play_sound(self, instance):
        self.GUI_Manager.setSoundOptions(EFFECT_DATA)
        self.GUI_Manager.toggleTokenOff()
        App.get_running_app().stop() 

    def open_popup(self, instance):
        popup = effectsPopUp(self)
        popup.open()

    def update_value_label(self):
        global EFFECT_DATA
        self.values = EFFECT_DATA.get_values()
        self.value_label.text = self.dict_to_str(self.values)
    
    def dict_to_str(self, dict):
        for each in dict:
            if type(dict[each]) == float:
                dict[each] = round(dict[each], 2)
        return '\n'.join(['{}: {}'.format(key, value) for key, value in dict.items()])

"""
Singleton class to store effect data

Don't make more than one instance of this class

"""
class EffectData():
    def __init__(self):
        self.data= {
            "reverse": {"value" : False, "type" : bool, "min" : None, "max" : None},
            "save": {"value" : False, "type" : bool, "min" : None, "max" : None},
            "crop_percent": {"value" : [0, 100], "type" : list, "min" : 0, "max" : 100},
            "transpose": {"value" : 0, "type" : int, "min" : -12, "max" : 12},
            "speed": {"value" : 1, "type" : float, "min" : 0.01, "max" : 5},
            "volume": {"value" : 1, "type" : float, "min" : 0.01, "max" : 5},
            # "start_percent": {"value" : 0, "type" : int, "min" : 0, "max" : 99},
            # "end_percent": {"value" : 100, "type" : int, "min" : 1, "max" : 100}       
        }

    def assign_value(self, key, value):
        self.data[key]["value"] = value
    
    def get_values(self):
        return {key : value["value"] for key, value in self.data.items()}

    def get_types(self):
        return {key : value["type"] for key, value in self.data.items()}
    
    def get_mins(self):
        return {key : value["min"] for key, value in self.data.items()}
    
    def get_maxs(self):
        return {key : value["max"] for key, value in self.data.items()}


class Settings(App):
    def __init__(self, commander, GUI_Manager):
        App.__init__(self)
        global EFFECT_DATA
        EFFECT_DATA = EffectData()
        self.GUI_Manager = GUI_Manager
        self.commander = commander
    
    def on_key_down(self, *args):  # Adjusted method signature to accept any number of arguments
        keyboard, keycode, text, modifiers = args[:4]
        # Check if the pressed key is the escape key (keycode 27)
        if keycode == 27:
            self.GUI_Manager.setSoundOptions(EFFECT_DATA)
            App.get_running_app().stop() 

    def build(self):
        Window.bind(on_key_down=self.on_key_down)
        return MainWindow(self.commander, self.GUI_Manager)
