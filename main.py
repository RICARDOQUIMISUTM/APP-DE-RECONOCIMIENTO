from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
from modules.ui.main_menu import MainMenuScreen
from modules.ui.register import RegisterScreen
from modules.ui.recognize import RecognizeScreen
from modules.ui.gallery import GalleryScreen
from modules.ui.export import ExportScreen
from modules.face_recognition.training import train_model
from modules.utils.file_io import ensure_export_folder
from kivy.logger import Logger
import os

class RootScreenManager(ScreenManager):
    pass

class FaceApp(App):
    def build(self):
        Logger.info("Iniciando aplicación")
        
        # Configuración de la ventana
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        
        # Crear carpetas necesarias
        ensure_export_folder()
        os.makedirs("data", exist_ok=True)
        os.makedirs("modelos/global", exist_ok=True)
        
        # Verificar y entrenar modelo inicial
        if not os.path.exists("modelos/global/recognizer.yml"):
            Logger.info("Modelo no encontrado. Entrenando modelo inicial...")
            train_model()

        # Configurar el administrador de pantallas
        sm = RootScreenManager()
        
        # Añadir todas las pantallas
        screens = [
            MainMenuScreen(name='main_menu'),
            RegisterScreen(name='register'),
            RecognizeScreen(name='recognize'),
            GalleryScreen(name='gallery'),
            ExportScreen(name='export')
        ]
        
        for screen in screens:
            sm.add_widget(screen)

        return sm

if __name__ == '__main__':
    FaceApp().run()