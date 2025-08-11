# modelos de datos sencillos (puede ampliarse)
class User:
    def __init__(self, user_id=None, name=None, created_at=None):
        self.user_id = user_id
        self.name = name
        self.created_at = created_at
