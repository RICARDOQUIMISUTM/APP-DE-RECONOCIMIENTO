from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from modules.database.operations import init_db
from modules.camera.camera_utils import camera_manager

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        init_db()
        
        # Configuración del layout principal
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Vista previa de la cámara
        self.camera_preview = Image(size_hint=(1, 0.7))
        layout.add_widget(self.camera_preview)
        
        # Botones del menú
        buttons = [
            ("Registrar Nuevo Usuario", 'register'),
            ("Reconocimiento Facial", 'recognize'),
            ("Galería de Usuarios", 'gallery'),
            ("Exportar Datos", 'export')
        ]
        
        for text, screen_name in buttons:
            btn = Button(
                text=text,
                size_hint=(1, 0.1),
                background_normal='',
                background_color=(0.2, 0.6, 0.8, 1)
            )
            btn.bind(on_press=lambda instance, sn=screen_name: self.go_to_screen(sn))
            layout.add_widget(btn)
        
        self.add_widget(layout)

    def on_enter(self):
        """Se ejecuta cuando la pantalla se muestra"""
        try:
            if camera_manager.open_camera():
                Clock.schedule_interval(self.update_camera, 1.0/30.0)  # 30 FPS
        except Exception as e:
            print(f"Error al iniciar cámara: {e}")

    def on_leave(self):
        """Se ejecuta cuando la pantalla se oculta"""
        Clock.unschedule(self.update_camera)
        camera_manager.release_camera()



    def go_to_screen(self, screen_name):
        """Navega a la pantalla especificada"""
        self.manager.current = screen_name