from datetime import datetime
from app import db
from models import User
from bson.objectid import ObjectId

projeto_collection = db['projetos']
user_collection = db['usuarios']  # Adicionei esta linha para a coleção de usuários

def criar_tarefas_gerais(lista_tarefas):
    todos_projetos = projeto_collection.find()

    for projeto in todos_projetos:
        id_projeto = projeto['_id']
        tarefas_existentes = {item['nome'] for item in projeto['itens']}

        for nome_tarefa in lista_tarefas:
            if nome_tarefa not in tarefas_existentes:
                novo_id = len(projeto['itens']) + 1
                print("\033[93m", f'Criando tarefa {nome_tarefa} ...', "\033[0m")
                projeto_collection.update_one(
                    {'_id': ObjectId(id_projeto)},
                    {'$push': {'itens': {'_id': novo_id, 'nome': nome_tarefa, 'feito': False}}}
                )

def criar_projetos_gerais(lista_projetos):
    projetos_existentes = {projeto['nome'] for projeto in projeto_collection.find()}

    for nome_projeto in lista_projetos:
        if nome_projeto not in projetos_existentes:
            print("\033[93m", f'Criando projeto {nome_projeto} ...', "\033[0m")
            projeto_collection.insert_one({
                'nome': nome_projeto,
                'itens': [],
                'status': 'Em Andamento',
                'data_criado': datetime.now()
            })


# Nova função para listar todos os usuários cadastrados
def listar_usuarios():
    users = user_collection.find()
    for user in users:
        print("\033[93m", f"Username: {user['username']}, Perfil: {user.get('perfil', 'N/A')}", "\033[0m")


# Nova função para apagar um usuário pelo username
def apagar_usuario(username):
    result = user_collection.delete_one({'username': username})
    if result.deleted_count:
        print("\033[92m", f"Usuário {username} apagado com sucesso!", "\033[0m")
    else:
        print("\033[91m", f"Usuário {username} não encontrado.", "\033[0m")
