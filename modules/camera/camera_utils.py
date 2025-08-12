import cv2
import platform
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.logger import Logger
from threading import Lock

class CameraManager:
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.cap = None
        self.active_screens = 0
        self._texture = None
        self._is_releasing = False

    def open_camera(self, start_index=0, max_index=5):
        with self._lock:
            if self._is_releasing:
                Logger.info("Cámara en proceso de liberación, esperando...")
                return False
                
            if self.cap is not None and self.cap.isOpened():
                self.active_screens += 1
                Logger.info(f"Cámara ya abierta (usuarios activos: {self.active_screens})")
                return True
                
            system = platform.system()
            backend = cv2.CAP_DSHOW if system == "Windows" else cv2.CAP_ANY
            
            for i in range(start_index, max_index + 1):
                try:
                    cap = cv2.VideoCapture(i, backend)
                    if cap.isOpened():
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        cap.set(cv2.CAP_PROP_FPS, 30)
                        self.cap = cap
                        self.active_screens = 1
                        Logger.info(f"✅ Cámara abierta en índice {i}")
                        return True
                    else:
                        cap.release()
                except Exception as e:
                    Logger.error(f"Error al abrir cámara en índice {i}: {str(e)}")
                    if 'cap' in locals():
                        cap.release()
            
            Logger.error("❌ No se pudo abrir ninguna cámara disponible.")
            return False
    
    def release_camera(self):
        with self._lock:
            if self.active_screens > 0:
                self.active_screens -= 1
                Logger.info(f"Cámara: Usuarios activos restantes: {self.active_screens}")
                
            if self.active_screens == 0 and self.cap is not None:
                self._is_releasing = True
                try:
                    self.cap.release()
                    self.cap = None
                    Logger.info("🔴 Cámara liberada correctamente")
                except Exception as e:
                    Logger.error(f"Error al liberar cámara: {str(e)}")
                finally:
                    self._is_releasing = False
    
    def read_frame(self):
        with self._lock:
            if self._is_releasing or self.cap is None or not self.cap.isOpened():
                return None
                
            try:
                ret, frame = self.cap.read()
                if ret:
                    # CORREGIR EL EFECTO ESPEJO AQUÍ
                    frame = cv2.flip(frame, 1)  # Volteo horizontal
                return frame if ret else None
            except Exception as e:
                Logger.error(f"Error al leer frame: {str(e)}")
                return None
    
    def frame_to_texture(self, frame):
        if frame is None:
            return None
            
        try:
            # Voltear verticalmente para corregir orientación en Kivy
            frame = cv2.flip(frame, 0)  # 0 = volteo vertical
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            buf = frame_rgb.tobytes()
            
            texture = Texture.create(
                size=(frame.shape[1], frame.shape[0]), 
                colorfmt='rgb'
            )
            texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')
            return texture
        except Exception as e:
            Logger.error(f"Error al convertir frame a textura: {str(e)}")
            return None

# Instancia global del administrador de cámara
camera_manager = CameraManager()