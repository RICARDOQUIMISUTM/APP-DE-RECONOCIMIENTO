from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from modules.ui.main_menu import MainMenuScreen
from modules.ui.register import RegisterScreen
from modules.ui.recognize import RecognizeScreen
from modules.ui.gallery import GalleryScreen
from modules.ui.export import ExportScreen
# Eliminar la importación de CameraPreviewScreen ya que está integrada en MainMenu

class RootScreenManager(ScreenManager):
    pass

class FaceApp(App):
    def build(self):
        sm = RootScreenManager()
        sm.add_widget(MainMenuScreen(name='main_menu'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(RecognizeScreen(name='recognize'))
        sm.add_widget(GalleryScreen(name='gallery'))
        sm.add_widget(ExportScreen(name='export'))
        return sm

if __name__ == '__main__':
    FaceApp().run()