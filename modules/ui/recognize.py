from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from modules.camera.camera_utils import camera_manager
from modules.face_recognition.detection import FaceDetector
from modules.face_recognition.recognition import FaceRecognizer
from modules.utils.file_io import list_user_photos
import cv2

class RecognizeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.detector = FaceDetector()
        self.recognizer = FaceRecognizer()
        self.img = Image()
        self.info = Label(text="Estado: listo", size_hint=(1, .1))
        self.gallery_label = Label(text="", size_hint=(1, .1))
        self.back_btn = Button(text="Volver", size_hint=(1, .1))
        self.back_btn.bind(on_press=self.go_back)

        # Configuración de la galería
        self.scroll = ScrollView()
        self.gallery_grid = GridLayout(
            cols=3, 
            spacing=5, 
            size_hint_y=None
        )
        self.gallery_grid.bind(
            minimum_height=self.gallery_grid.setter('height')
        )
        self.scroll.add_widget(self.gallery_grid)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.img)
        layout.add_widget(self.info)
        layout.add_widget(self.gallery_label)
        layout.add_widget(self.scroll)
        layout.add_widget(self.back_btn)
        self.add_widget(layout)
        
        self.current_user = None

    def on_enter(self):
        try:
            if camera_manager.open_camera():
                Clock.schedule_interval(self.update, 1.0/15.0)
                self.clear_gallery()
        except Exception as e:
            self.info.text = f"Error cámara: {str(e)}"

    def on_leave(self):
        Clock.unschedule(self.update)
        camera_manager.release_camera()
        self.clear_gallery()

    def update(self, dt):
        frame = camera_manager.read_frame()
        if frame is None:
            return
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detect(gray)
        
        if faces is not None and len(faces) > 0:
            (x,y,w,h) = faces[0]
            roi = gray[y:y+h, x:x+w]
            name, conf = self.recognizer.predict(roi)
            
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
            cv2.putText(
                frame, 
                f"{name}", 
                (x, y-10), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, 
                (255,255,255), 
                2
            )
            conf_text = f"{conf:.1f}" if conf is not None else "-"
            cv2.putText(
                frame, 
                f"Conf: {conf_text}", 
                (x, y+h+20), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                (255,255,0), 
                1
            )
            
            if name and name != self.current_user:
                self.current_user = name
                self.update_gallery(name)
        else:
            if self.current_user is not None:
                self.clear_gallery()
                self.current_user = None
        
        self.img.texture = camera_manager.frame_to_texture(frame)

    def update_gallery(self, user_name):
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
        self.manager.current = 'main_menu'