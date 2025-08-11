from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.logger import Logger
from modules.camera.camera_utils import camera_manager
from modules.face_recognition.detection import FaceDetector
from modules.face_recognition.recognition import FaceRecognizer
from modules.utils.file_io import list_user_photos
import cv2

class RecognizeScreen(Screen):
    img = ObjectProperty(None)
    info = ObjectProperty(None)
    gallery_label = ObjectProperty(None)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.detector = FaceDetector()
        self.recognizer = FaceRecognizer()
        self.current_user = None
        self._camera_clock = None
        
        # Configuración de la interfaz
        layout = BoxLayout(orientation='vertical')
        
        # Vista de la cámara
        self.img = Image(size_hint=(1, 0.6))
        layout.add_widget(self.img)
        
        # Etiqueta de información
        self.info = Label(
            text="Estado: listo", 
            size_hint=(1, 0.1),
            font_size='16sp'
        )
        layout.add_widget(self.info)
        
        # Etiqueta de galería
        self.gallery_label = Label(
            text="", 
            size_hint=(1, 0.1),
            font_size='14sp'
        )
        layout.add_widget(self.gallery_label)
        
        # Galería de fotos del usuario
        self.scroll = ScrollView(size_hint=(1, 0.5))
        self.gallery_grid = GridLayout(cols=3, spacing=5, size_hint_y=None)
        self.gallery_grid.bind(minimum_height=self.gallery_grid.setter('height'))
        self.scroll.add_widget(self.gallery_grid)
        layout.add_widget(self.scroll)
        
        # Botón de volver
        self.back_btn = Button(
            text="Volver al Menú",
            size_hint=(1, 0.1),
            background_normal='',
            background_color=(0.8, 0.3, 0.3, 1)
        )
        self.back_btn.bind(on_press=self.go_back)
        layout.add_widget(self.back_btn)
        
        self.add_widget(layout)

    def on_enter(self):
        """Se ejecuta cuando la pantalla se muestra"""
        Logger.info("PantallaReconocimiento: Iniciando...")
        try:
            # Asegurar que tenemos la última versión del reconocedor
            from modules.face_recognition.recognition import FaceRecognizer
            self.recognizer = FaceRecognizer()
            
            if camera_manager.open_camera():
                self._camera_clock = Clock.schedule_interval(self.update, 1.0/15.0)
        except Exception as e:
            Logger.error(f"Error al iniciar reconocimiento: {str(e)}")
            self.info.text = f"Error: {str(e)}"

    def on_leave(self):
        """Se ejecuta cuando la pantalla se oculta"""
        Logger.info("PantallaReconocimiento: Ocultando pantalla de reconocimiento")
        if self._camera_clock:
            Clock.unschedule(self._camera_clock)
        camera_manager.release_camera()
        self.clear_gallery()

    def update(self, dt):
        """Actualización con manejo de errores mejorado"""
        try:
            frame = camera_manager.read_frame()
            if frame is None:
                return
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector.detect(gray)
            
            if faces is not None and len(faces) > 0:
                (x, y, w, h) = faces[0]
                roi = gray[y:y+h, x:x+w]
                
                # Usar el reconocedor actualizado
                name, conf = self.recognizer.predict(roi)
                
                # Dibujar resultados
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                text = f"{name} ({conf:.1f}%)" if conf else name
                cv2.putText(frame, text, (x, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                if name != "Desconocido" and name != self.current_user:
                    self.current_user = name
                    self.update_gallery(name)
            else:
                if self.current_user is not None:
                    self.clear_gallery()
                    self.current_user = None
            
            self.img.texture = camera_manager.frame_to_texture(frame)
        except Exception as e:
            Logger.error(f"Error en update: {str(e)}")
    def update_gallery(self, user_name):
        """Actualiza la galería con las fotos del usuario reconocido"""
        self.gallery_grid.clear_widgets()
        photos = list_user_photos(user_name=user_name)
        
        if not photos:
            self.gallery_label.text = f"{user_name}: No hay fotos"
            return
            
        self.gallery_label.text = f"Galería de {user_name}:"
        for photo_path in photos[:9]:  # Mostrar máximo 9 fotos
            img = Image(
                source=photo_path, 
                size_hint_y=None, 
                height=100
            )
            self.gallery_grid.add_widget(img)

    def clear_gallery(self):
        """Limpia la galería y restablece los textos"""
        self.gallery_grid.clear_widgets()
        self.gallery_label.text = ""
        self.current_user = None
        self.info.text = "Estado: listo"

    def go_back(self, instance):
        """Regresa al menú principal"""
        self.manager.current = 'main_menu'