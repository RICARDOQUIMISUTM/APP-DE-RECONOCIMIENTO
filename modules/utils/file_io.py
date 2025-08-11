import os
import shutil

def ensure_user_folder(base="data", user_name=None):
    if user_name is None or user_name.strip() == "":
        raise ValueError("user_name requerido")
    folder = os.path.join(base, user_name)
    os.makedirs(folder, exist_ok=True)
    return folder

def list_user_photos(base="data", user_name=None):
    folder = os.path.join(base, user_name)
    if not os.path.exists(folder):
        return []
    return sorted([os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(('.png','.jpg','.jpeg'))])

def export_folder(destination, source="data"):
    if not os.path.exists(source):
        return False
    shutil.make_archive(destination, 'zip', source)
    return True
