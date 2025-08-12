from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock
from modules.ui.main_menu import MainMenuScreen
from modules.ui.register import RegisterScreen
from modules.ui.recognize import RecognizeScreen
from modules.ui.gallery import GalleryScreen
from modules.ui.export import ExportScreen
import os

class RootScreenManager(ScreenManager):
    pass

class FaceApp(App):
    def build(self):
        # Crear carpetas necesarias
        os.makedirs("data", exist_ok=True)
        os.makedirs("modelos/global", exist_ok=True)
        
        # Configurar el administrador de pantallas
        sm = RootScreenManager()
        
        # Añadir pantallas con carga progresiva
        screens = [
            ('main_menu', MainMenuScreen),
            ('register', RegisterScreen),
            ('recognize', RecognizeScreen),
            ('gallery', GalleryScreen),
            ('export', ExportScreen)
        ]
        
        # Cargar pantallas una por una con retraso
        def load_screens(index):
            if index < len(screens):
                name, screen_class = screens[index]
                sm.add_widget(screen_class(name=name))
                Clock.schedule_once(lambda dt: load_screens(index + 1), 0.1)
        
        load_screens(0)
        return sm

if __name__ == '__main__':
    FaceApp().run()