import os
import cv2
import numpy as np
from modules.database.operations import list_users, init_db

MODEL_DIR = "modelos"
GLOBAL_MODEL_PATH = os.path.join(MODEL_DIR, "global", "recognizer.yml")
LABEL_MAP_FILE = os.path.join(MODEL_DIR, "global", "label_map.txt")

def ensure_model_dir():
    os.makedirs(os.path.join(MODEL_DIR, "global"), exist_ok=True)

def train_model():
    """Entrena el modelo global con todos los usuarios"""
    init_db()
    ensure_model_dir()
    faces = []
    labels = []
    label_map = {}
    label_id = 0

    users = list_users()
    if not users:
        print("⚠ No hay usuarios para entrenar")
        return False

    for user_id, user_name, _, _ in users:
        user_dir = os.path.join("data", user_name)
        if not os.path.exists(user_dir):
            continue

        label_map[label_id] = user_name
        photos = [f for f in os.listdir(user_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        
        for photo in photos:
            img_path = os.path.join(user_dir, photo)
            try:
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img = cv2.resize(img, (200, 200))
                    img = cv2.equalizeHist(img)
                    faces.append(img)
                    labels.append(label_id)
            except Exception as e:
                print(f"Error procesando {img_path}: {e}")

        label_id += 1

    if not faces:
        print("⚠ No se encontraron imágenes válidas para entrenar")
        return False

    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.train(faces, np.array(labels))
        
        # Guardar modelo y mapeo de etiquetas
        recognizer.save(GLOBAL_MODEL_PATH)
        
        with open(LABEL_MAP_FILE, "w", encoding="utf-8") as f:
            for id_, name in label_map.items():
                f.write(f"{id_},{name}\n")
        
        print(f"✅ Modelo entrenado con {len(faces)} imágenes de {len(label_map)} usuarios")
        return True
    except Exception as e:
        print(f"❌ Error al entrenar modelo: {e}")
        return False