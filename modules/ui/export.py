from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from modules.utils.file_io import export_folder, list_user_photos
from modules.database.operations import list_users
import os
import shutil
import tempfile

class ExportScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=8, spacing=8)

        # Selector de usuario
        self.user_spinner = Spinner(
            text='Seleccionar usuario',
            values=['Todos'] + [user[1] for user in list_users()],
            size_hint=(1, .1)
        )

        # Entrada para nombre de archivo
        self.dest_input = TextInput(
            text="export_data",
            hint_text="Nombre del archivo (sin extensión)",
            size_hint=(1, .1)
        )

        # Botones de acción
        btn_export = Button(
            text="Exportar selección",
            size_hint=(1, .1)
        )
        btn_export.bind(on_press=self.export_selection)

        btn_back = Button(text="Volver", size_hint=(1, .1))
        btn_back.bind(on_press=self.go_back)

        # Mensaje de estado
        self.status_label = Label(text="", size_hint=(1, .1))

        layout.add_widget(Label(text="Seleccione usuario a exportar:"))
        layout.add_widget(self.user_spinner)
        layout.add_widget(Label(text="Nombre del archivo de salida:"))
        layout.add_widget(self.dest_input)
        layout.add_widget(btn_export)
        layout.add_widget(self.status_label)
        layout.add_widget(btn_back)
        self.add_widget(layout)

    def export_selection(self, *args):
        user = self.user_spinner.text
        dest = self.dest_input.text.strip() or "export_data"

        if user == "Todos":
            ok = export_folder(destination=dest, source="data")
            if ok:
                self.status_label.text = f"✅ Todos los datos exportados a {dest}.zip"
            else:
                self.status_label.text = "❌ Error al exportar todos los datos"
        else:
            photos = list_user_photos(user_name=user)
            if not photos:
                self.status_label.text = f"⚠ No hay fotos para {user}"
                return

            tmp = tempfile.mkdtemp()
            userfolder = os.path.join(tmp, user)
            os.makedirs(userfolder, exist_ok=True)
            
            for p in photos:
                shutil.copy(p, os.path.join(userfolder, os.path.basename(p)))
            
            shutil.make_archive(dest, 'zip', tmp)
            shutil.rmtree(tmp)
            self.status_label.text = f"✅ {user} exportado a {dest}.zip"

    def go_back(self, *args):
        self.manager.current = 'main_menu'