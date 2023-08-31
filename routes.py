from flask import render_template, request, redirect, url_for, jsonify
from flask_login import login_user, logout_user
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from models import User
from bson.objectid import ObjectId

projeto_collection = db['projetos']
user_collection = db['usuarios']


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        novo_projeto = request.form.get('newProjectName')

        now = datetime.now()
        formatted_date = now.strftime("%d/%m/%Y às %H:%M")

        print("\033[92m", formatted_date, "\033[0m")
        projeto_collection.insert_one({'nome': novo_projeto, 'itens': [], 'status': 'Em Andamento',
                                       'data_criado': formatted_date})
        return redirect(url_for('index'))

    projetos = list(projeto_collection.find())
    return render_template('index.html', projetos=projetos)


@app.route('/projeto/<id_projeto>', methods=['GET', 'POST'])
def projeto(id_projeto):
    if request.method == 'POST':
        novo_item = request.form.get('nome_item')
        projeto = projeto_collection.find_one({'_id': ObjectId(id_projeto)})

        # Gerar um novo ObjectId para a tarefa
        novo_id = ObjectId()

        projeto_collection.update_one(
            {'_id': ObjectId(id_projeto)},
            {'$push': {'itens': {'_id': novo_id, 'nome': novo_item, 'feito': False}}}
        )
        return redirect(url_for('index'))

    projeto = projeto_collection.find_one({'_id': ObjectId(id_projeto)})
    return render_template('projeto.html', projeto=projeto)


@app.route('/excluir_projeto/<id_projeto>', methods=['POST'])
def excluir_projeto(id_projeto):
    projeto_collection.delete_one({'_id': ObjectId(id_projeto)})
    return redirect(url_for('index'))


@app.route('/excluir_tarefa/<id_projeto>/<id_tarefa>', methods=['POST'])
def excluir_tarefa(id_projeto, id_tarefa):
    try:
        id_tarefa = int(id_tarefa)  # Convertendo para int; mude isso de acordo com o tipo de ID que você está usando
    except ValueError:
        return "ID da tarefa inválido", 400

    try:
        projeto_collection.update_one(
            {'_id': ObjectId(id_projeto)},
            {'$pull': {'itens': {'_id': id_tarefa}}}
        )
    except Exception as e:
        return str(e), 500
    return redirect(url_for('index'))


@app.route('/update_tarefa/<id_projeto>/<id_tarefa>', methods=['POST'])
def update_tarefa(id_projeto, id_tarefa):
    print("\033[96m", id_projeto, '-', id_tarefa, "\033[0m")
    try:
        novo_estado = request.json['feito']
    except KeyError:
        return jsonify({"error": "Parâmetro 'feito' não fornecido"}), 400

    try:
        projeto_collection.update_one(
            {'_id': ObjectId(id_projeto), 'itens._id': ObjectId(id_tarefa)},
            {'$set': {'itens.$.feito': novo_estado}}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"success": True})


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Buscar usuário no banco de dados
        user_data = user_collection.find_one({"username": username})
        if user_data and check_password_hash(user_data["password"], password):
            user = User(user_data)
            login_user(user)
            print(f'Usuário {username} logado com sucesso.')
            return redirect(url_for('index'))
        else:
            print('Credenciais inválidas')
            return 'Credenciais inválidas', 400

    return render_template('login.html')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        perfil = request.form.get('perfil')

        hashed_password = generate_password_hash(password, method='sha256')

        # Validações básicas (melhorar isso)
        if not username or not password or not perfil:
            return "Preencha todos os campos", 400

        # Verificar se o usuário já existe
        if user_collection.find_one({'username': username}):
            return "Nome de usuário já existe", 400

        # Inserir o novo usuário
        user_collection.insert_one({
            'username': username,
            'password': hashed_password,  # Agora é o hash da senha
            'perfil': perfil,
            'data_criado': datetime.now()
        })
        print("\033[92m", f'Cadastro de {username} criado com sucesso...', "\033[0m")
        return redirect(url_for('index'))

    return render_template('cadastro.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))