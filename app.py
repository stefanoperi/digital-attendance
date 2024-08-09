
from app_resources import AppResources
from kivy.uix.screenmanager import ScreenManager, Screen
from main_sc import MainScreen
from capturer_sc import CapturerScreen
from kivy.app import App

class DigitalAttendanceApp(App):
    def build(self):
        # Create the resources object
        resources = AppResources()

        # Create the screen manager
        self.sm = ScreenManager()
   
        # Create the main screen and add it to the ScreenManager
        main_screen = Screen(name='main')
        main_screen_widget = MainScreen(transition_callback=self.transition_to, resources=resources)
        main_screen.add_widget(main_screen_widget)
        self.sm.add_widget(main_screen)
        
        # Create the capturer screen and add it to the ScreenManager
        capturer_screen = Screen(name='capturer')
        capturer_screen_widget= CapturerScreen(main_screen=main_screen_widget, resources=resources)
        capturer_screen.add_widget(capturer_screen_widget)
        self.sm.add_widget(capturer_screen)

        # Set the initial screen to the main screen
        self.sm.current = 'main'

        return self.sm

    def transition_to(self, screen_name, *args):
        self.sm.current = screen_name

if __name__ == '__main__':
    DigitalAttendanceApp().run()
