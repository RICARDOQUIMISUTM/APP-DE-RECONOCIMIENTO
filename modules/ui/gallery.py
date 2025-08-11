from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from modules.database.operations import list_users
from modules.utils.file_io import list_user_photos
import os

class GalleryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        # Controles superiores
        top = BoxLayout(size_hint=(1, .1))
        self.filter_input = TextInput(hint_text="Filtrar por usuario", size_hint=(.6, 1))
        btn_filter = Button(text="Filtrar", size_hint=(.2, 1))
        btn_filter.bind(on_press=lambda x: self.apply_filter())  # Corregido aquí
        btn_refresh = Button(text="Refrescar", size_hint=(.2, 1))
        btn_refresh.bind(on_press=lambda x: self.build_gallery())  # Corregido aquí
        btn_back = Button(text="Volver", size_hint=(.2, 1))
        btn_back.bind(on_press=lambda x: self.go_back())  # Corregido aquí
        
        top.add_widget(self.filter_input)
        top.add_widget(btn_filter)
        top.add_widget(btn_refresh)
        top.add_widget(btn_back)
        layout.add_widget(top)

        # Galería principal
        self.scroll = ScrollView()
        self.grid = GridLayout(cols=4, spacing=5, size_hint_y=None)
        self.grid.bind(minimum_height=self.grid.setter('height'))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)

        self.add_widget(layout)
        self.build_gallery()

    def build_gallery(self, filter_user=None):
        self.grid.clear_widgets()
        users = list_users()
        
        if not users:
            self.grid.add_widget(Label(text="No hay usuarios ni fotos"))
            return
            
        for _id, name, created_at in users:
            if filter_user and filter_user.lower() not in name.lower():
                continue
                
            # Mostrar usuario y fecha
            user_label = Label(text=f"{name}\n{created_at[:10]}", size_hint_y=None, height=50)
            self.grid.add_widget(user_label)
            
            # Mostrar fotos del usuario
            photos = list_user_photos(user_name=name)
            for p in photos[:4]:  # Mostrar máximo 4 fotos por usuario
                img = Image(source=p, size_hint_y=None, height=150)
                img.bind(on_touch_down=lambda instance, touch: self.show_full_image(instance.source) 
                         if instance.collide_point(*touch.pos) else None)
                self.grid.add_widget(img)

    def apply_filter(self):
        filter_text = self.filter_input.text.strip()
        self.build_gallery(filter_user=filter_text)

    def show_full_image(self, image_path):
        content = BoxLayout(orientation='vertical')
        img = Image(source=image_path)
        btn_close = Button(text="Cerrar", size_hint=(1, .1))
        
        popup = Popup(title=os.path.basename(image_path), size_hint=(.8, .8))
        content.add_widget(img)
        content.add_widget(btn_close)
        popup.content = content
        
        btn_close.bind(on_press=popup.dismiss)
        popup.open()

    def go_back(self):
        self.manager.current = 'main_menu'