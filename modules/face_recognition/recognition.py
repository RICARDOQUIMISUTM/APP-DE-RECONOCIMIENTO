import os
import cv2
from kivy.logger import Logger

class FaceRecognizer:
    def __init__(self):
        """Inicializa el reconocedor facial cargando el modelo si existe"""
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.label_map = {}
        self.is_trained = False
        self.model_path = "modelos/global/recognizer.yml"
        self.label_map_path = "modelos/global/label_map.txt"
        self.load_model()

    def load_model(self):
        """Carga el modelo entrenado desde los archivos"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.label_map_path):
                Logger.info("Cargando modelo de reconocimiento facial...")
                self.recognizer.read(self.model_path)
                self.label_map = {}
                
                with open(self.label_map_path, "r", encoding="utf-8") as f:
                    for line in f:
                        id_s, name = line.strip().split(",", 1)
                        self.label_map[int(id_s)] = name
                
                self.is_trained = True
                Logger.info(f"✅ Modelo cargado correctamente. {len(self.label_map)} usuarios registrados")
                return True
            else:
                Logger.warning("⚠ Modelo no encontrado, necesita entrenamiento")
                self.is_trained = False
                return False
        except Exception as e:
            Logger.error(f"❌ Error al cargar modelo: {e}")
            self.is_trained = False
            return False

    def reload_model(self):
        """Recarga el modelo desde disco para obtener los últimos cambios"""
        Logger.info("Recargando modelo de reconocimiento...")
        try:
            return self.load_model()
        except Exception as e:
            Logger.error(f"Error al recargar modelo: {e}")
            return False

    def predict(self, face_image):
        """
        Realiza predicción sobre una imagen de rostro
        Args:
            face_image: Imagen del rostro (BGR o escala de grises)
        Returns:
            tuple: (nombre, confianza) o ("Desconocido", None) si no entrenado
        """
        if not self.is_trained:
            return "Desconocido", None
        
        try:
            # Preprocesamiento de la imagen
            if len(face_image.shape) == 3:
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:
                gray = face_image
            
            if gray.shape != (200, 200):
                gray = cv2.resize(gray, (200, 200))
            
            # Realizar predicción
            label_id, confidence = self.recognizer.predict(gray)
            name = self.label_map.get(label_id, f"Desconocido ({label_id})")
            
            # Ajustar confianza para ser más intuitiva (menor es mejor)
            adjusted_confidence = 100 - confidence if confidence is not None else None
            return name, adjusted_confidence
        except Exception as e:
            Logger.error(f"Error en predicción: {e}")
            return "Desconocido", None