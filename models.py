
from flask_login import UserMixin


class CustomUserMixin(UserMixin):
    def __init__(self, is_active=True, **kwargs):
        super().__init__(**kwargs)
        self._is_active = is_active

    @property
    def is_active(self):
        return self._is_active


class User(CustomUserMixin):
    def __init__(self, user_data):  # user_data é o dicionário obtido do MongoDB
        self.id = str(user_data["_id"])  # Convertendo ObjectId para string
        self.username = user_data["username"]
        self.password = user_data["password"]
        self.email = user_data.get("email")  # O método get() retornará None se "email" não estiver presente
        super().__init__(is_active=user_data.get("is_active", True))
