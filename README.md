# Sistema de Reconocimiento Facial

Aplicación de reconocimiento facial con funciones de registro, identificación, gestión de usuarios y exportación de datos. Desarrollada con Python, Kivy para la interfaz gráfica y OpenCV para el procesamiento de imágenes.

- Registrar nuevos usuarios con fotos faciales
- Identificar personas en tiempo real
- Gestionar galerías de fotos por usuario
- Exportar datos a archivos

## Interpreter

**Python:** Python3.10.11

## Instalación

### 1 Clonar el repositorio:

```bash
git clone https://github.com/RICARDOQUIMISUTM/APP-DE-RECONOCIMIENTO.git
```

### 2 Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate    # Windows
```

### 3 Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4 Uso de la Aplicación

```bash
python main.py
```

### Estructura de Archivos

```bash
app/
├── data/           # Base de datos y fotos de usuarios
├── modelos/        # Archivos exportados
├── modules/
│   ├── camera/     # Manejo de cámara
│   ├── database/   # Operaciones con DB
│   ├── face_recognition/   # Lógica de reconocimiento
│   ├── ui/         # Interfaces gráficas
│   └── utils/
├── main.py         # Punto de entrada
├── readme.md
├──requirements.txt
└── assets         # Recursos estáticos

```

## License

[MIT](https://choosealicense.com/licenses/mit/)
