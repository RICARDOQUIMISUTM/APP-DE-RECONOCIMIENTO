import cv2
import platform
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.logger import Logger

class CameraManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.cap = None
            cls._instance.active_screens = 0
        return cls._instance
    
    def open_camera(self, start_index=0, max_index=5):
        if self.cap is not None and self.cap.isOpened():
            self.active_screens += 1
            Logger.info(f"Cámara: Ya está abierta (usuarios activos: {self.active_screens})")
            return True
            
        system = platform.system()
        backend = cv2.CAP_DSHOW if system == "Windows" else cv2.CAP_ANY
        
        for i in range(start_index, max_index + 1):
            try:
                cap = cv2.VideoCapture(i, backend)
                if cap.isOpened():
                    # Configuración estándar para la mayoría de cámaras
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
                if cap:
                    cap.release()
        
        Logger.error("❌ No se pudo abrir ninguna cámara disponible.")
        return False
    
    def release_camera(self):
        if self.active_screens > 0:
            self.active_screens -= 1
            Logger.info(f"Cámara: Usuarios activos restantes: {self.active_screens}")
            
        if self.active_screens == 0 and self.cap is not None:
            self.cap.release()
            self.cap = None
            Logger.info("🔴 Cámara liberada")
    
    def read_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        if not ret:
            Logger.warning("No se pudo leer frame de la cámara")
            return None
        return frame
    def frame_to_texture(self, frame):
        if frame is None:
             return None
        try:
        # Convertir de BGR a RGB (OpenCV usa BGR por defecto)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Aplicar flip vertical para corregir la orientación
            frame_corrected = cv2.flip(frame_rgb, 0)  # 0 = flip vertical
        
        # Crear textura Kivy
            buf = frame_corrected.tobytes()
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