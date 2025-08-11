from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.button import Button
from kivy.clock import Clock
from modules.camera.camera_utils import camera_manager  # Importación actualizada

class CameraPreviewScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.img = Image()
        self.back_btn = Button(text="Volver", size_hint=(1, .1))
        self.back_btn.bind(on_press=self.go_back)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.img)
        layout.add_widget(self.back_btn)
        self.add_widget(layout)

    def on_enter(self):
        """Se ejecuta cuando la pantalla se muestra"""
        try:
            if camera_manager.open_camera():
                Clock.schedule_interval(self.update, 1.0/15.0)
        except Exception as e:
            print(f"Error al abrir cámara: {str(e)}")

    def on_leave(self):
        """Se ejecuta cuando la pantalla se oculta"""
        Clock.unschedule(self.update)
        camera_manager.release_camera()

    def update(self, dt):
        frame = camera_manager.read_frame()
        if frame is not None:
            self.img.texture = camera_manager.frame_to_texture(frame)

    def go_back(self, instance):
        self.manager.current = 'main_menu'