from flask import Flask
from flask_login import LoginManager
from mongo_connection import get_mongo_client
from bson.objectid import ObjectId


app = Flask(__name__)
app.secret_key = 'b7fe60d9148d4a4c8b7a06c8d0a10f3b'

login_manager = LoginManager()
login_manager.init_app(app)

client = get_mongo_client()
db = client['MeuChecklist']

user_collection = db['usuarios']


from routes import *
from utils import *


@login_manager.user_loader
def load_user(user_id):
    user_data = user_collection.find_one({"_id": ObjectId(user_id)})
    if not user_data:
        return None
    return User(user_data)


if __name__ == "__main__":
    #listar_usuarios()
    #apagar_usuario('')
    #listar_projetos()
    app.run(debug=True)
