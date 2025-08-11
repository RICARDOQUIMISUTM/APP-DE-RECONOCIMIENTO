import os
import shutil
from datetime import datetime

def ensure_user_folder(base_dir="data", user_name=None):
    """
    Crea una carpeta para un usuario si no existe
    
    Args:
        base_dir: Directorio base (default: "data")
        user_name: Nombre del usuario (requerido)
    
    Returns:
        str: Ruta completa a la carpeta del usuario
    
    Raises:
        ValueError: Si user_name no es válido
    """
    if not user_name or not isinstance(user_name, str):
        raise ValueError("Se requiere un nombre de usuario válido")
    
    # Limpiar nombre para usar como directorio
    safe_name = "".join(c for c in user_name if c.isalnum() or c in (' ', '_', '-')).strip()
    if not safe_name:
        raise ValueError("El nombre de usuario no puede estar vacío")
    
    user_folder = os.path.join(base_dir, safe_name)
    os.makedirs(user_folder, exist_ok=True)
    return user_folder

def ensure_export_folder():
    """
    Crea la carpeta de exportaciones si no existe
    
    Returns:
        str: Ruta a la carpeta exports
    """
    export_dir = os.path.join("exports")
    os.makedirs(export_dir, exist_ok=True)
    return export_dir

def list_user_photos(user_name, base_dir="data"):
    """
    Lista todas las fotos de un usuario
    
    Args:
        user_name: Nombre del usuario
        base_dir: Directorio base (default: "data")
    
    Returns:
        list: Lista ordenada de rutas a fotos
    """
    user_dir = os.path.join(base_dir, user_name)
    if not os.path.exists(user_dir):
        return []
    
    photos = []
    valid_ext = ('.png', '.jpg', '.jpeg')
    
    for f in sorted(os.listdir(user_dir)):
        if f.lower().endswith(valid_ext):
            photos.append(os.path.join(user_dir, f))
    
    return photos

def export_user_data(user_name=None):
    """
    Exporta datos a la carpeta exports
    
    Args:
        user_name: Nombre de usuario (None para exportar todos)
    
    Returns:
        str: Ruta del archivo ZIP creado
    """
    export_dir = ensure_export_folder()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if user_name:
        # Exportar usuario específico
        source_dir = os.path.join("data", user_name)
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"No existe el usuario: {user_name}")
        
        zip_name = f"export_{user_name}_{timestamp}.zip"
        export_path = os.path.join(export_dir, zip_name)
        shutil.make_archive(export_path[:-4], 'zip', source_dir)
    else:
        # Exportar todos los usuarios
        zip_name = f"export_all_{timestamp}.zip"
        export_path = os.path.join(export_dir, zip_name)
        shutil.make_archive(export_path[:-4], 'zip', "data")
    
    return export_path

def count_user_photos(user_name, base_dir="data"):
    """Cuenta las fotos de un usuario"""
    return len(list_user_photos(user_name, base_dir))

def get_all_users(base_dir="data"):
    """Obtiene lista de todos los usuarios registrados"""
    if not os.path.exists(base_dir):
        return []
    
    return [d for d in os.listdir(base_dir) 
           if os.path.isdir(os.path.join(base_dir, d))]