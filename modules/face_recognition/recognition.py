import os
import cv2

class FaceRecognizer:
    def __init__(self):
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.label_map = {}
        self.is_trained = False
        self.load_model()

    def load_model(self):
        """Carga el modelo entrenado si existe"""
        model_path = "modelos/global/recognizer.yml"
        label_path = "modelos/global/label_map.txt"
        
        if os.path.exists(model_path) and os.path.exists(label_path):
            try:
                self.recognizer.read(model_path)
                
                with open(label_path, "r", encoding="utf-8") as f:
                    for line in f:
                        id_s, name = line.strip().split(",", 1)
                        self.label_map[int(id_s)] = name
                
                self.is_trained = True
                print("✅ Modelo cargado correctamente")
            except Exception as e:
                print(f"❌ Error al cargar modelo: {e}")
                self.is_trained = False
        else:
            print("⚠ Modelo no encontrado, necesita entrenamiento")
            self.is_trained = False

    def predict(self, face_image):
        """
        Realiza predicción solo si el modelo está entrenado
        Args:
            face_image: Imagen del rostro (BGR o escala de grises)
        Returns:
            tuple: (nombre, confianza) o ("Desconocido", None) si no entrenado
        """
        if not self.is_trained:
            return "Desconocido", None
        
        try:
            # Convertir a escala de grises si es necesario
            if len(face_image.shape) == 3:  # Imagen BGR
                gray = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
            else:  # Ya está en escala de grises
                gray = face_image
            
            # Redimensionar si es necesario
            if gray.shape != (200, 200):
                gray = cv2.resize(gray, (200, 200))
            
            # Realizar predicción
            label_id, confidence = self.recognizer.predict(gray)
            name = self.label_map.get(label_id, f"Desconocido ({label_id})")
            return name, confidence
        except Exception as e:
            print(f"Error en predicción: {e}")
            return "Desconocido", None