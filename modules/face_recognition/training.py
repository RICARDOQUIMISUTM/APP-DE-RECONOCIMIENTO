import os
import cv2
import numpy as np
from modules.database.operations import list_users, init_db
from kivy.logger import Logger

MODEL_DIR = "modelos"
GLOBAL_MODEL_PATH = os.path.join(MODEL_DIR, "global", "recognizer.yml")
LABEL_MAP_FILE = os.path.join(MODEL_DIR, "global", "label_map.txt")

def ensure_model_dir():
    """Crea la estructura de directorios para los modelos si no existe"""
    os.makedirs(os.path.join(MODEL_DIR, "global"), exist_ok=True)

def train_model():
    """Entrenamiento con verificación de datos"""
    try:
        init_db()
        ensure_model_dir()
        
        # Verificar que hay datos suficientes
        users = list_users()
        if not users:
            Logger.error("No hay usuarios para entrenar")
            return False
            
        # Colectar datos
        faces, labels, label_map = [], [], {}
        label_id = 0
        
        for user_id, user_name, _, _ in users:
            user_dir = os.path.join("data", user_name)
            if not os.path.exists(user_dir):
                continue
                
            photos = [f for f in os.listdir(user_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            if not photos:
                continue
                
            label_map[label_id] = user_name
            
            for photo in photos:
                img_path = os.path.join(user_dir, photo)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img = cv2.resize(img, (200, 200))
                    img = cv2.equalizeHist(img)
                    faces.append(img)
                    labels.append(label_id)
            
            label_id += 1

        if len(faces) < 2:  # Mínimo 2 imágenes para entrenar
            Logger.error(f"No hay suficientes imágenes ({len(faces)}) para entrenar")
            return False

        # Entrenar y guardar
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(labels))
        
        # Guardar en archivo temporal primero
        temp_model = f"{GLOBAL_MODEL_PATH}.tmp"
        recognizer.save(temp_model)
        
        # Reemplazar archivos atómicamente
        import shutil
        shutil.move(temp_model, GLOBAL_MODEL_PATH)
        
        # Guardar etiquetas
        with open(LABEL_MAP_FILE, "w", encoding="utf-8") as f:
            for id_, name in label_map.items():
                f.write(f"{id_},{name}\n")
        
        Logger.info(f"Modelo entrenado con {len(faces)} imágenes de {len(label_map)} usuarios")
        return True
        
    except Exception as e:
        Logger.error(f"Error crítico en entrenamiento: {e}")
        return False