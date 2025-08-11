import os
import cv2
import numpy as np
from kivy.logger import Logger
from threading import Lock

class FaceRecognizer:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.label_map = {}
        self.is_trained = False
        self.model_path = "modelos/global/recognizer.yml"
        self.label_map_path = "modelos/global/label_map.txt"
        self._load_model()

    def _load_model(self):
        """Carga el modelo de manera segura con bloqueo"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.label_map_path):
                Logger.info("Cargando modelo de reconocimiento...")
                
                # Crear nuevo reconocedor para evitar problemas de referencia
                new_recognizer = cv2.face.LBPHFaceRecognizer_create()
                new_recognizer.read(self.model_path)
                
                # Cargar nuevo mapeo de etiquetas
                new_label_map = {}
                with open(self.label_map_path, "r", encoding="utf-8") as f:
                    for line in f:
                        id_s, name = line.strip().split(",", 1)
                        new_label_map[int(id_s)] = name
                
                # Actualizar en un solo paso atómico
                with self._lock:
                    self.recognizer = new_recognizer
                    self.label_map = new_label_map
                    self.is_trained = True
                
                Logger.info(f"✅ Modelo cargado. {len(new_label_map)} usuarios registrados")
                return True
            else:
                Logger.warning("⚠ Modelo no encontrado")
                return False
        except Exception as e:
            Logger.error(f"❌ Error cargando modelo: {e}")
            return False

    def reload_model(self):
        """Recarga el modelo de manera segura"""
        Logger.info("Solicitada recarga del modelo...")
        return self._load_model()

    def predict(self, face_image):
        """
        Predicción segura con bloqueo
        Args:
            face_image: Imagen del rostro (BGR o escala de grises)
        Returns:
            tuple: (nombre, confianza) o ("Desconocido", None)
        """
        with self._lock:
            if not self.is_trained:
                return "Desconocido", None
            
            try:
                # Preprocesamiento
                if len(face_image.shape) == 3:
                    gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
                else:
                    gray = face_image
                
                gray = cv2.resize(gray, (200, 200))
                
                # Predicción
                label_id, confidence = self.recognizer.predict(gray)
                name = self.label_map.get(label_id, "Desconocido")
                
                # Ajustar confianza (menor es mejor)
                adjusted_conf = 100 - confidence if confidence <= 100 else 0
                return name, adjusted_conf
            except Exception as e:
                Logger.error(f"Error en predicción: {e}")
                return "Desconocido", None