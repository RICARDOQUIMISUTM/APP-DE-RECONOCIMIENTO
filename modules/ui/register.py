from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.logger import Logger
from modules.camera.camera_utils import camera_manager
from modules.face_recognition.detection import FaceDetector
from modules.utils.file_io import ensure_user_folder
from modules.database.operations import add_user, increment_photo_count, user_exists
from modules.face_recognition.training import train_model
import cv2
import os

class RegisterScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.detector = FaceDetector()
        
        # Layout principal
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        
        # Vista previa de la cámara
        self.camera_preview = Image(size_hint=(1, 0.7))
        layout.add_widget(self.camera_preview)
        
        # Entrada de nombre
        self.name_input = TextInput(
            hint_text="Ingrese nombre completo",
            multiline=False,
            size_hint=(1, 0.1),
            font_size='18sp',
            background_color=(1, 1, 1, 0.8),
            foreground_color=(0, 0, 0, 1)
        )
        layout.add_widget(self.name_input)
        
        # Etiqueta de estado
        self.status_label = Label(
            text="[b]Estado:[/b] Listo para registrar",
            markup=True,
            size_hint=(1, 0.1),
            color=(0.1, 0.1, 0.1, 1),
            font_size='16sp'
        )
        layout.add_widget(self.status_label)
        
        # Botones
        btn_layout = BoxLayout(size_hint=(1, 0.2), spacing=10)
        
        # Botón de captura automática
        self.auto_capture_btn = Button(
            text="Captura Automática",
            background_normal='',
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.auto_capture_btn.bind(on_press=self.start_auto_capture)
        
        # Botón de captura manual
        self.manual_capture_btn = Button(
            text="Captura Manual", 
            background_normal='',
            background_color=(0.3, 0.5, 0.8, 1)
        )
        self.manual_capture_btn.bind(on_press=self.manual_capture)
        
        # Botón de volver
        self.back_btn = Button(
            text="Volver", 
            background_normal='',
            background_color=(0.8, 0.3, 0.3, 1)
        )
        self.back_btn.bind(on_press=self.go_back)
        
        btn_layout.add_widget(self.auto_capture_btn)
        btn_layout.add_widget(self.manual_capture_btn)
        btn_layout.add_widget(self.back_btn)
        
        layout.add_widget(btn_layout)
        self.add_widget(layout)
        
        # Variables de control
        self.capture_counter = 0
        self.max_captures = 20
        self.is_capturing = False
        self._camera_clock = None
        self._capture_clock = None

    def on_enter(self):
        """Se ejecuta cuando la pantalla se muestra"""
        Logger.info("Registro: Entrando a pantalla de registro")
        try:
            if camera_manager.open_camera():
                self._camera_clock = Clock.schedule_interval(self.update_camera, 1.0/30.0)
                self.status_label.text = "[b]Estado:[/b] Cámara activa - Posicione el rostro"
                self.status_label.color = (0.1, 0.1, 0.1, 1)
        except Exception as e:
            Logger.error(f"Registro: Error al iniciar cámara: {str(e)}")
            self.status_label.text = f"[b]Error:[/b] {str(e)}"
            self.status_label.color = (0.8, 0.2, 0.2, 1)

    def on_leave(self):
        """Se ejecuta cuando la pantalla se oculta"""
        Logger.info("Registro: Saliendo de pantalla de registro")
        if self._camera_clock:
            Clock.unschedule(self._camera_clock)
        if self._capture_clock:
            Clock.unschedule(self._capture_clock)
        camera_manager.release_camera()
        self.is_capturing = False
        self.capture_counter = 0

    def update_camera(self, dt):
        """Actualiza la vista previa de la cámara"""
        try:
            frame = camera_manager.read_frame()
            if frame is None:
                return
                
            # Detección de rostros
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detector.detect(gray)
            
            # Dibujar rectángulo alrededor del rostro
            if faces is not None and len(faces) > 0:
                (x, y, w, h) = faces[0]
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Mostrar contador durante captura automática
                if self.is_capturing:
                    cv2.putText(frame, f"Capturas: {self.capture_counter}/{self.max_captures}", 
                               (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            
            # Actualizar vista previa
            texture = camera_manager.frame_to_texture(frame)
            if texture:
                self.camera_preview.texture = texture
        except Exception as e:
            Logger.error(f"Registro: Error en update_camera: {str(e)}")

    def start_auto_capture(self, instance):
        """Inicia el proceso de captura automática"""
        user_name = self.name_input.text.strip()
        
        if not user_name:
            self.status_label.text = "[b]Error:[/b] Ingrese un nombre válido"
            self.status_label.color = (0.8, 0.2, 0.2, 1)
            return
            
        if not self.validate_username(user_name):
            return
            
        # Registrar usuario en la base de datos
        if not add_user(user_name):
            self.status_label.text = "[b]Error:[/b] Usuario ya existe o no se pudo registrar"
            self.status_label.color = (0.8, 0.2, 0.2, 1)
            return
            
        try:
            user_folder = ensure_user_folder(user_name=user_name)
            self.status_label.text = f"[b]Estado:[/b] Capturando {self.max_captures} fotos para {user_name}..."
            self.status_label.color = (0.2, 0.6, 0.2, 1)
            
            self.is_capturing = True
            self.capture_counter = 0
            self._capture_clock = Clock.schedule_interval(
                lambda dt: self.capture_face(user_folder, user_name), 
                0.5
            )
        except Exception as e:
            Logger.error(f"Registro: Error en start_auto_capture: {str(e)}")
            self.status_label.text = f"[b]Error:[/b] {str(e)}"
            self.status_label.color = (0.8, 0.2, 0.2, 1)

    def validate_username(self, user_name):
        """Valida el nombre de usuario"""
        if not user_name.replace(" ", "").isalnum():
            self.status_label.text = "[b]Error:[/b] Solo use letras y números"
            self.status_label.color = (0.8, 0.2, 0.2, 1)
            return False
            
        if len(user_name) < 3:
            self.status_label.text = "[b]Error:[/b] Nombre muy corto (min 3 caracteres)"
            self.status_label.color = (0.8, 0.2, 0.2, 1)
            return False
            
        return True

    def capture_face(self, user_folder, user_name):
        """Captura un rostro y guarda la imagen"""
        if not self.is_capturing or self.capture_counter >= self.max_captures:
            if self._capture_clock:
                Clock.unschedule(self._capture_clock)
                self._capture_clock = None
            self.finish_registration(user_name)
            return
            
        frame = camera_manager.read_frame()
        if frame is None:
            return
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detect(gray)
        
        if faces is not None and len(faces) > 0:
            try:
                roi = cv2.resize(gray[faces[0][1]:faces[0][1]+faces[0][3], 
                                faces[0][0]:faces[0][0]+faces[0][2]], 
                                (200, 200))
                img_path = os.path.join(user_folder, f"{self.capture_counter+1}.jpg")
                cv2.imwrite(img_path, roi)
                increment_photo_count(user_name)
                self.capture_counter += 1
            except Exception as e:
                Logger.error(f"Registro: Error al guardar imagen: {e}")

    def manual_capture(self, instance):
        """Captura manual de un solo rostro"""
        user_name = self.name_input.text.strip()
        
        if not user_name:
            self.status_label.text = "[b]Error:[/b] Ingrese un nombre válido"
            self.status_label.color = (0.8, 0.2, 0.2, 1)
            return
            
        if not self.validate_username(user_name):
            return
            
        # Registrar usuario en la base de datos si no existe
        if not user_exists(user_name) and not add_user(user_name):
            self.status_label.text = "[b]Error:[/b] No se pudo registrar usuario"
            self.status_label.color = (0.8, 0.2, 0.2, 1)
            return
            
        frame = camera_manager.read_frame()
        if frame is None:
            self.status_label.text = "[b]Error:[/b] No se pudo capturar imagen"
            self.status_label.color = (0.8, 0.2, 0.2, 1)
            return
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector.detect(gray)
        
        if faces is None or len(faces) == 0:
            self.status_label.text = "[b]Error:[/b] No se detectó rostro"
            self.status_label.color = (0.8, 0.2, 0.2, 1)
            return
            
        try:
            user_folder = ensure_user_folder(user_name=user_name)
            existing_photos = len([f for f in os.listdir(user_folder) 
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            roi = cv2.resize(gray[faces[0][1]:faces[0][1]+faces[0][3], 
                            faces[0][0]:faces[0][0]+faces[0][2]], 
                            (200, 200))
            img_path = os.path.join(user_folder, f"{existing_photos+1}.jpg")
            cv2.imwrite(img_path, roi)
            increment_photo_count(user_name)
            
            # Entrenar modelo
            if train_model():
                self.status_label.text = f"[b]Éxito:[/b] Foto de {user_name} guardada"
                self.status_label.color = (0.2, 0.7, 0.2, 1)
            else:
                self.status_label.text = "[b]Error:[/b] Foto guardada pero falló el entrenamiento"
                self.status_label.color = (0.8, 0.2, 0.2, 1)
        except Exception as e:
            Logger.error(f"Registro: Error en manual_capture: {str(e)}")
            self.status_label.text = f"[b]Error:[/b] {str(e)}"
            self.status_label.color = (0.8, 0.2, 0.2, 1)

    def finish_registration(self, user_name):
        """Finaliza el registro y entrena el modelo"""
        self.is_capturing = False
        
        if self.capture_counter > 0:
            # Entrenar modelo
            if train_model():
                self.status_label.text = f"[b]Éxito:[/b] {user_name} registrado con {self.capture_counter} fotos"
                self.status_label.color = (0.2, 0.7, 0.2, 1)
            else:
                self.status_label.text = "[b]Error:[/b] Fotos guardadas pero falló el entrenamiento"
                self.status_label.color = (0.8, 0.2, 0.2, 1)
        else:
            self.status_label.text = "[b]Error:[/b] No se capturaron fotos válidas"
            self.status_label.color = (0.8, 0.2, 0.2, 1)

    def go_back(self, instance):
        """Regresa al menú principal"""
        self.manager.current = 'main_menu'