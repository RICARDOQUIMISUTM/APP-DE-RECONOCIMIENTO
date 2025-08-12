import os
import cv2
import threading
import time
from kivy.logger import Logger
from kivy.clock import Clock
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
        self.is_loading = False
        self.model_path = "modelos/global/recognizer.yml"
        self.label_map_path = "modelos/global/label_map.txt"
        
        # Carga inicial en segundo plano
        self._start_async_load()

    def _start_async_load(self):
        """Inicia la carga del modelo en segundo plano"""
        if self.is_loading:
            return
            
        self.is_loading = True
        Logger.info("Iniciando carga asíncrona del modelo...")
        
        def load_task():
            try:
                if os.path.exists(self.model_path) and os.path.exists(self.label_map_path):
                    # Cargar en un reconocedor temporal
                    temp_recognizer = cv2.face.LBPHFaceRecognizer_create()
                    temp_recognizer.read(self.model_path)
                    
                    # Cargar etiquetas
                    temp_label_map = {}
                    with open(self.label_map_path, "r", encoding="utf-8") as f:
                        for line in f:
                            id_s, name = line.strip().split(",", 1)
                            temp_label_map[int(id_s)] = name
                    
                    # Actualizar en el hilo principal
                    def update_ui():
                        with self._lock:
                            self.recognizer = temp_recognizer
                            self.label_map = temp_label_map
                            self.is_trained = True
                            self.is_loading = False
                        Logger.info("✅ Modelo cargado correctamente")
                    
                    Clock.schedule_once(lambda dt: update_ui())
                else:
                    Logger.warning("Archivos del modelo no encontrados")
                    self.is_loading = False
            except Exception as e:
                Logger.error(f"Error cargando modelo: {str(e)}")
                self.is_loading = False

        # Ejecutar en un hilo separado
        threading.Thread(target=load_task, daemon=True).start()

    def reload_model(self):
        """Recarga el modelo en segundo plano"""
        if not self.is_loading:
            self._start_async_load()
        return True

    def predict(self, face_image):
        """Predicción segura con verificación de carga"""
        with self._lock:
            if not self.is_trained:
                return "Modelo cargando...", None
                
            try:
                gray = face_image if len(face_image.shape) == 2 else \
                       cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, (200, 200))
                
                label_id, confidence = self.recognizer.predict(gray)
                name = self.label_map.get(label_id, "Desconocido")
                return name, (100 - confidence) if confidence <= 100 else 0
            except Exception as e:
                Logger.error(f"Error en predicción: {str(e)}")
                return "Error", None