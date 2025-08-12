import os
import cv2
import time  # Importación añadida
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
    """Entrenamiento optimizado"""
    try:
        start_time = time.time()
        Logger.info("Iniciando entrenamiento...")
        
        # Colectar datos
        faces, labels, label_map = [], [], {}
        label_id = 0
        
        # Limitar tamaño de imágenes para entrenamiento
        MAX_IMAGES_PER_USER = 50  
        
        for user_id, user_name, _, _ in list_users():
            user_dir = os.path.join("data", user_name)
            if not os.path.exists(user_dir):
                continue
                
            photos = [f for f in os.listdir(user_dir) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg'))][:MAX_IMAGES_PER_USER]
            
            if not photos:
                continue
                
            label_map[label_id] = user_name
            
            for photo in photos:
                img_path = os.path.join(user_dir, photo)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img = cv2.resize(img, (200, 200))
                    faces.append(img)
                    labels.append(label_id)
            
            label_id += 1

        if len(faces) < 2:
            Logger.error("Insuficientes imágenes para entrenar")
            return False

        # Entrenamiento con progreso
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        Logger.info(f"Entrenando con {len(faces)} imágenes...")
        recognizer.train(faces, np.array(labels))
        
        # Guardar modelo temporal
        temp_path = f"{GLOBAL_MODEL_PATH}.tmp"
        recognizer.save(temp_path)
        
        # Reemplazar atómicamente
        import shutil
        shutil.move(temp_path, GLOBAL_MODEL_PATH)
        
        # Guardar etiquetas
        with open(LABEL_MAP_FILE, "w", encoding="utf-8") as f:
            for id_, name in label_map.items():
                f.write(f"{id_},{name}\n")
        
        Logger.info(f"Entrenamiento completado en {time.time()-start_time:.2f}s")
        return True
        
    except Exception as e:
        Logger.error(f"Error en entrenamiento: {str(e)}")
        return False
   