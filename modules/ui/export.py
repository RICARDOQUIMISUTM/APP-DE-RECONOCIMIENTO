from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from modules.database.operations import list_users
from modules.utils.file_io import export_user_data
import os

class ExportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.add_widget(self.layout)
        self.build_ui()
        
    def build_ui(self):
        self.layout.clear_widgets()
        
        # Título
        title = Label(
            text="Exportar Datos",
            size_hint=(1, 0.1),
            font_size='20sp',
            bold=True
        )
        self.layout.add_widget(title)
        
        # Selector de usuario
        self.user_spinner = Spinner(
            text='Seleccionar usuario',
            values=['Todos los usuarios'] + [user[1] for user in list_users()],
            size_hint=(1, 0.1),
            background_color=(0.9, 0.9, 0.9, 1)
        )
        self.layout.add_widget(self.user_spinner)
        
        # Botón de exportación
        btn_export = Button(
            text="Exportar",
            size_hint=(1, 0.1),
            background_normal='',
            background_color=(0.2, 0.7, 0.3, 1)
        )
        btn_export.bind(on_press=self.export_data)
        self.layout.add_widget(btn_export)
        
        # Estado de la exportación
        self.status_label = Label(
            text="",
            size_hint=(1, 0.1),
            color=(0.8, 0.2, 0.2, 1)
        )
        self.layout.add_widget(self.status_label)
        
        # Botón de volver
        btn_back = Button(
            text="Volver al Menú",
            size_hint=(1, 0.1),
            background_normal='',
            background_color=(0.8, 0.3, 0.3, 1)
        )
        btn_back.bind(on_press=self.go_back)
        self.layout.add_widget(btn_back)
    
    def on_enter(self):
        """Actualiza la lista de usuarios cuando se entra a la pantalla"""
        self.build_ui()

    def export_data(self, instance):
        selected = self.user_spinner.text
        user_name = None if selected == 'Todos los usuarios' else selected
        
        try:
            export_path = export_user_data(user_name)
            
            if export_path:
                file_size = os.path.getsize(export_path) / (1024 * 1024)  # Tamaño en MB
                self.status_label.text = f"Exportado: {os.path.basename(export_path)}\nTamaño: {file_size:.2f} MB"
                self.status_label.color = (0.2, 0.7, 0.3, 1)
            else:
                self.status_label.text = "Error: No se pudo exportar"
                self.status_label.color = (0.8, 0.2, 0.2, 1)
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"
            self.status_label.color = (0.8, 0.2, 0.2, 1)

    def go_back(self, instance):
        self.manager.current = 'main_menu'