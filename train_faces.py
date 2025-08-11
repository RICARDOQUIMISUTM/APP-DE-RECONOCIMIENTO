import os
import cv2
import numpy as np

def train():
    faces = []
    labels = []
    label_id = 0
    label_map = {}
    base_path = 'data/'

    # Verificar si hay datos para entrenar
    if not os.path.exists(base_path) or not os.listdir(base_path):
        print("No hay datos de entrenamiento en la carpeta 'data'")
        return

    for person_name in os.listdir(base_path):
        person_path = os.path.join(base_path, person_name)
        if not os.path.isdir(person_path):
            continue
            
        label_map[label_id] = person_name
        for img_name in os.listdir(person_path):
            img_path = os.path.join(person_path, img_name)
            image = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                continue
                
            # Redimensionar si es necesario
            if image.shape[0] > 500 or image.shape[1] > 500:
                image = cv2.resize(image, (200, 200))
                
            faces.append(image)
            labels.append(label_id)
        
        label_id += 1

    if len(faces) == 0:
        print("No hay imágenes válidas para entrenar!")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))
    os.makedirs("modelos", exist_ok=True)
    recognizer.save("modelos/recognizer.yml")
    
    # Guardar el mapeo de etiquetas
    with open("modelos/label_map.txt", "w") as f:
        for id, name in label_map.items():
            f.write(f"{id},{name}\n")
    
    print(f"Entrenamiento completado con {len(faces)} imágenes de {len(label_map)} personas")

if __name__ == '__main__':
    train()