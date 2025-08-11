import os
import cv2
import numpy as np

MODEL_DIR = "modelos"
MODEL_FILE = os.path.join(MODEL_DIR, "recognizer.yml")
LABEL_MAP_FILE = os.path.join(MODEL_DIR, "label_map.txt")

def train_from_folder(data_folder="data"):
    faces = []
    labels = []
    label_map = {}
    label_id = 0

    if not os.path.exists(data_folder):
        print("❌ Carpeta de datos no existe:", data_folder)
        return False

    people = [d for d in os.listdir(data_folder) if os.path.isdir(os.path.join(data_folder, d))]
    if not people:
        print("⚠ No hay subcarpetas de usuarios en 'data/'.")
        return False

    for person in people:
        person_path = os.path.join(data_folder, person)
        label_map[label_id] = person
        for fname in os.listdir(person_path):
            fpath = os.path.join(person_path, fname)
            img = cv2.imread(fpath, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            img = cv2.resize(img, (200, 200))
            faces.append(img)
            labels.append(label_id)
        label_id += 1

    if not faces:
        print("⚠ No se encontraron imágenes válidas para entrenar.")
        return False

    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
    except Exception as e:
        print("❌ cv2.face no disponible o error:", e)
        return False

    recognizer.train(faces, np.array(labels))
    os.makedirs(MODEL_DIR, exist_ok=True)
    recognizer.save(MODEL_FILE)

    with open(LABEL_MAP_FILE, "w", encoding="utf-8") as f:
        for id_, name in label_map.items():
            f.write(f"{id_},{name}\n")

    print(f"✅ Entrenamiento completado: {len(faces)} imágenes, {len(label_map)} usuarios")
    return True
