from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from modules.camera.camera_utils import camera_manager
from modules.face_recognition.detection import FaceDetector
from modules.utils.file_io import ensure_user_folder
from modules.utils.helpers import crop_face_from_frame
from modules.database.operations import add_user, list_users
import cv2
import os

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.detector = FaceDetector()
        self.img = Image()
        self.name_input = TextInput(
            hint_text="Nombre del usuario", 
            multiline=False, 
            size_hint=(1, .1)
        )
        self.capture_btn = Button(
            text="Capturar foto", 
            size_hint=(1, .1)
        )
        self.capture_btn.bind(on_press=self.manual_capture)
        self.back_btn = Button(
            text="Volver", 
            size_hint=(1, .1)
        )
        self.back_btn.bind(on_press=self.go_back)
        self.status_label = Label(
            text="Estado: Esperando entrada", 
            size_hint=(1, .1)
        )

        # Autocompletado de usuarios existentes
        self.existing_users = [user[1] for user in list_users()]
        self.name_input.bind(text=self.on_text)

        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.img)
        layout.add_widget(self.name_input)
        layout.add_widget(self.status_label)
        layout.add_widget(self.capture_btn)
        layout.add_widget(self.back_btn)
        self.add_widget(layout)

    def on_enter(self):
        try:
            if camera_manager.open_camera():
                Clock.schedule_interval(self.update, 1.0/15.0)
        except Exception as e:
            self.status_label.text = f"Error cámara: {str(e)}"

    def on_leave(self):
        Clock.unschedule(self.update)
        camera_manager.release_camera()

    def on_text(self, instance, value):
        if value in self.existing_users:
            self.status_label.text = f"Usuario existente: {value}"
        else:
            self.status_label.text = "Nuevo usuario"

    def update(self, dt):
        frame = camera_manager.read_frame()
        if frame is None:
            return
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detect(gray)
        
        if faces is not None and len(faces) > 0:
            for (x,y,w,h) in faces:
                cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2)
        
        self.img.texture = camera_manager.frame_to_texture(frame)

    def manual_capture(self, instance):
        frame = camera_manager.read_frame()
        if frame is None:
            self.status_label.text = "Error: No se pudo capturar"
            return
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detect(gray)
        
        if faces is None or len(faces) == 0:
            self.status_label.text = "Error: No se detectó rostro"
            return
            
        user = self.name_input.text.strip()
        if not user:
            self.status_label.text = "Error: Ingresa un nombre"
            return
            
        try:
            roi = crop_face_from_frame(frame, faces[0])
            folder = ensure_user_folder(user_name=user)
            existing_photos = [f for f in os.listdir(folder) 
                             if f.lower().endswith(('.jpg','.png','.jpeg'))]
            target = os.path.join(folder, f"{len(existing_photos)+1}.jpg")
            cv2.imwrite(target, roi)
            add_user(user)
            self.status_label.text = f"Foto guardada: {target}"
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"

    def go_back(self, instance):
        self.manager.current = 'main_menu'