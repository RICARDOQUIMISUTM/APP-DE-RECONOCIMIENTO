import os
import cv2

MODEL_DIR = "modelos"
MODEL_FILE = os.path.join(MODEL_DIR, "recognizer.yml")
LABEL_MAP_FILE = os.path.join(MODEL_DIR, "label_map.txt")

class FaceRecognizer:
    def __init__(self):
        self.recognizer = None
        self.label_map = {}
        self._create_recognizer()
        self.load()

    def _create_recognizer(self):
        try:
            self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        except Exception:
            try:
                self.recognizer = cv2.createLBPHFaceRecognizer()
            except Exception:
                self.recognizer = None
                print("⚠ Aviso: cv2.face LBPH no disponible. Reconocimiento desactivado.")

    def load(self):
        # Cargar modelo entrenado
        if self.recognizer and os.path.exists(MODEL_FILE):
            try:
                self.recognizer.read(MODEL_FILE)
            except Exception as e:
                print("Error cargando modelo:", e)

        # Cargar mapa de etiquetas
        self.label_map.clear()
        if os.path.exists(LABEL_MAP_FILE):
            with open(LABEL_MAP_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    id_s, name = line.strip().split(",", 1)
                    self.label_map[int(id_s)] = name

    def predict(self, face_roi):
        """
        face_roi: imagen en escala de grises del rostro recortado.
        Retorna (nombre_usuario, confianza) o (None, None) si no disponible.
        """
        if not self.recognizer:
            return None, None
        try:
            label_id, confidence = self.recognizer.predict(face_roi)
            name = self.label_map.get(label_id, f"Desconocido ({label_id})")
            return name, confidence
        except Exception as e:
            print("Error en predicción:", e)
            return None, None
