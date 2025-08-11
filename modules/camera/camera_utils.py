import cv2
import platform
from kivy.graphics.texture import Texture

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
            return True
            
        system = platform.system()
        backend = cv2.CAP_DSHOW if system == "Windows" else None
        
        for i in range(start_index, max_index + 1):
            cap = cv2.VideoCapture(i, backend) if backend else cv2.VideoCapture(i)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap = cap
                self.active_screens = 1
                print(f"✅ Cámara abierta en índice {i}")
                return True
            else:
                cap.release()
        
        raise RuntimeError("❌ No se pudo abrir ninguna cámara disponible.")
    
    def release_camera(self):
        if self.active_screens > 0:
            self.active_screens -= 1
            
        if self.active_screens == 0 and self.cap is not None:
            self.cap.release()
            self.cap = None
            print("🔴 Cámara liberada")
    
    def read_frame(self):
        if self.cap is None or not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        return frame if ret else None
    
    def frame_to_texture(self, frame):
        if frame is None:
            return None
        flipped = cv2.flip(frame, 0)
        buf = flipped.tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
        texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
        return texture

# Instancia global del administrador de cámara
camera_manager = CameraManager()