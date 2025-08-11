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
    """Entrena el modelo global con todos los usuarios registrados"""
    init_db()
    ensure_model_dir()
    faces = []
    labels = []
    label_map = {}
    label_id = 0

    # Obtener todos los usuarios de la base de datos
    users = list_users()
    if not users:
        Logger.warning("⚠ No hay usuarios para entrenar")
        return False

    Logger.info(f"Iniciando entrenamiento para {len(users)} usuarios...")
    
    for user_id, user_name, _, _ in users:
        user_dir = os.path.join("data", user_name)
        if not os.path.exists(user_dir):
            Logger.warning(f"No se encontraron fotos para {user_name}")
            continue

        label_map[label_id] = user_name
        photos = [f for f in os.listdir(user_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        if not photos:
            Logger.warning(f"Usuario {user_name} no tiene fotos válidas")
            continue

        Logger.info(f"Procesando {len(photos)} fotos de {user_name}...")
        
        for photo in photos:
            img_path = os.path.join(user_dir, photo)
            try:
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    # Preprocesamiento de la imagen
                    img = cv2.resize(img, (200, 200))
                    img = cv2.equalizeHist(img)  # Normalización de contraste
                    faces.append(img)
                    labels.append(label_id)
            except Exception as e:
                Logger.error(f"Error procesando {img_path}: {e}")

        label_id += 1

    if not faces:
        Logger.error("⚠ No se encontraron imágenes válidas para entrenar")
        return False

    try:
        # Crear y entrenar el modelo
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(labels))
        
        # Guardar modelo entrenado
        recognizer.save(GLOBAL_MODEL_PATH)
        
        # Guardar mapeo de etiquetas
        with open(LABEL_MAP_FILE, "w", encoding="utf-8") as f:
            for id_, name in label_map.items():
                f.write(f"{id_},{name}\n")
        
        Logger.info(f"✅ Modelo entrenado con {len(faces)} imágenes de {len(label_map)} usuarios")
        return True
    except Exception as e:
        Logger.error(f"❌ Error al entrenar modelo: {e}")
        return False