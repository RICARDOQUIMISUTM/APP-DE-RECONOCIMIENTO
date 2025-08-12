from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window
from modules.camera.camera_utils import camera_manager
from modules.face_recognition.recognition import FaceRecognizer
from kivy.logger import Logger
import threading

class MainMenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera_preview = None
        self._camera_clock = None
        self._model_check_clock = None
        self.buttons_created = False
        
        # Layout principal con fondo
        self.layout = BoxLayout(orientation='vertical')
        self._set_background()
        
        # Panel de estado superior
        self.status_panel = BoxLayout(size_hint=(1, 0.1))
        self.status_label = Label(
            text="Inicializando sistema...",
            font_size='16sp',
            color=(1, 1, 1, 1)
        )
        self.status_panel.add_widget(self.status_label)
        self.layout.add_widget(self.status_panel)
        
        # Contenedor de contenido central
        self.content_container = BoxLayout(size_hint=(1, 0.8))
        self.layout.add_widget(self.content_container)
        
        # Panel de carga inicial
        self._show_loading_screen()
        
        self.add_widget(self.layout)
        
        # Iniciar verificación del modelo
        self._model_check_clock = Clock.schedule_interval(self._check_model_status, 0.5)
        
        # Iniciar cámara en segundo plano
        threading.Thread(target=self._initialize_camera, daemon=True).start()

    def _set_background(self):
        """Configura el fondo de pantalla"""
        with self.layout.canvas.before:
            Color(0.1, 0.1, 0.1, 1)
            self.bg_rect = Rectangle(
                size=Window.size,
                pos=self.layout.pos
            )
        
        self.layout.bind(size=self._update_bg_rect)

    def _update_bg_rect(self, instance, value):
        """Actualiza el tamaño del fondo"""
        self.bg_rect.size = value

    def _show_loading_screen(self):
        """Muestra la pantalla de carga inicial"""
        self.content_container.clear_widgets()
        
        loading_layout = BoxLayout(
            orientation='vertical',
            spacing=20,
            padding=40
        )
        
        self.loading_label = Label(
            text="Cargando módulos principales...",
            font_size='18sp',
            color=(1, 1, 1, 1)
        )
        
        loading_layout.add_widget(self.loading_label)
        self.content_container.add_widget(loading_layout)

    def _initialize_camera(self):
        """Inicializa la cámara con manejo robusto de errores"""
        try:
            if camera_manager.open_camera():
                # Programar la vista previa en el hilo principal
                Clock.schedule_once(self._start_camera_preview)
            else:
                self._update_status("Cámara no disponible", (0.8, 0.2, 0.2, 1))
        except Exception as e:
            Logger.error(f"Error crítico al iniciar cámara: {str(e)}")
            self._update_status(f"Error cámara: {str(e)}", (0.8, 0.2, 0.2, 1))

    def _start_camera_preview(self, dt):
        """Inicia la vista previa de la cámara"""
        if self.camera_preview is None:
            self.camera_preview = Image(size_hint=(1, 0.7))
            self._camera_clock = Clock.schedule_interval(self._update_camera, 1.0/30.0)

    def _update_camera(self, dt):
        """Actualiza la vista previa de la cámara"""
        if self.camera_preview and self.camera_preview.parent:
            frame = camera_manager.read_frame()
            if frame is not None:
                self.camera_preview.texture = camera_manager.frame_to_texture(frame)

    def _check_model_status(self, dt):
        """Verifica el estado del modelo de reconocimiento"""
        recognizer = FaceRecognizer()
        
        if recognizer.is_trained and not self.buttons_created:
            self._update_status("Sistema listo", (0.2, 0.8, 0.2, 1))
            Clock.schedule_once(self._create_main_interface)
            Clock.unschedule(self._model_check_clock)
        elif recognizer.is_loading:
            self._update_status("Cargando modelo facial...", (0.9, 0.6, 0.1, 1))
        else:
            self._update_status("Preparando reconocimiento...", (0.9, 0.6, 0.1, 1))

    def _update_status(self, text, color):
        """Actualiza el mensaje de estado"""
        if hasattr(self, 'status_label'):
            self.status_label.text = text
            self.status_label.color = color

    def _create_main_interface(self, dt):
        """Crea la interfaz principal una vez cargado todo"""
        self.content_container.clear_widgets()
        
        main_layout = BoxLayout(orientation='vertical', spacing=10)
        
        # Vista previa de la cámara
        if self.camera_preview is None:
            self.camera_preview = Image(size_hint=(1, 0.7))
        main_layout.add_widget(self.camera_preview)
        
        # Botones del menú
        buttons = [
            ("Registrar Nuevo Usuario", 'register', (0.2, 0.6, 0.8, 1)),
            ("Reconocimiento Facial", 'recognize', (0.3, 0.5, 0.8, 1)),
            ("Galería de Usuarios", 'gallery', (0.4, 0.4, 0.8, 1)),
            ("Exportar Datos", 'export', (0.5, 0.3, 0.8, 1))
        ]
        
        for text, screen_name, color in buttons:
            btn = Button(
                text=text,
                size_hint=(1, 0.1),
                background_normal='',
                background_color=color,
                font_size='16sp',
                color=(1, 1, 1, 1)
            )
            btn.bind(on_press=lambda instance, sn=screen_name: self._go_to_screen(sn))
            main_layout.add_widget(btn)
        
        self.content_container.add_widget(main_layout)
        self.buttons_created = True

    def _go_to_screen(self, screen_name):
        """Navega a la pantalla especificada"""
        self.manager.current = screen_name

    def on_enter(self):
        """Al entrar a la pantalla"""
        if not hasattr(self, '_camera_clock') or self._camera_clock is None:
            self._camera_clock = Clock.schedule_interval(self._update_camera, 1.0/30.0)
        
        # Reabrir cámara si es necesario
        if camera_manager.active_screens == 0:
            threading.Thread(target=self._initialize_camera, daemon=True).start()

    def on_leave(self):
        """Al salir de la pantalla"""
        if hasattr(self, '_camera_clock') and self._camera_clock:
            Clock.unschedule(self._camera_clock)
            self._camera_clock = None
        if hasattr(self, 'camera_preview') and self.camera_preview.parent:
                self.content_container.remove_widget(self.camera_preview)  
                          
        camera_manager.release_camera()