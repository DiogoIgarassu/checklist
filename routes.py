from flask import render_template, request, redirect, url_for, jsonify, send_file, Response
from flask_login import login_user, logout_user, current_user
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from models import User
from bson.objectid import ObjectId
import pdfkit
import tempfile
import pandas as pd
import os
os.environ['QT_QPA_PLATFORM'] = 'wayland'

projeto_collection = db['projetos']
user_collection = db['usuarios']


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        novo_projeto = request.form.get('newProjectName')

        now = datetime.now()
        formatted_date = now.strftime("%d/%m/%Y às %H:%M")

        if novo_projeto:
            username = "Guest"  # Usuário padrão se ninguém estiver logado
            if current_user and current_user.is_authenticated:
                username = current_user.username

            print("\033[92m", f"O usuário {username} adicionou o projeto {novo_projeto} em {formatted_date}", "\033[0m")
            projeto_collection.insert_one({'nome': novo_projeto, 'itens': [], 'status': 'Em Andamento',
                                           'data_criado': formatted_date})
            return redirect(url_for('index'))

    projetos = list(projeto_collection.find())
    projetos_pessoais = ['Artista Manoel Santos', 'Artista Micheal Jakson', 'Artista Janderson Nobre', 'Artista Rosa Santos']

    # Verificar se o usuário está logado
    if not current_user.is_authenticated:  # Substitua esta linha pelo seu método de verificação
        projetos = [proj for proj in projetos if proj['nome'] not in projetos_pessoais]
    #print("\033[95m", projetos[0])

    # Ordenação manual em Python
    projetos.sort(key=lambda x: x['nome'].lower())

    return render_template('index.html', projetos=projetos)


@app.route('/edit_task/<projeto_id>/<item_id>', methods=['POST'])
def edit_task(projeto_id, item_id):
    edited_task_name = request.form.get('editedTaskName')

    if edited_task_name:
        # Atualizar o nome da tarefa no banco de dados
        result = projeto_collection.update_one(
            {'_id': ObjectId(projeto_id), 'itens._id': ObjectId(item_id)},
            {'$set': {'itens.$.nome': edited_task_name}}
        )

        if result.matched_count > 0:
            print("\033[92m", f"Tarefa {item_id} atualizada com sucesso para {edited_task_name}", "\033[0m")
        else:
            print("\033[91m", "Nenhum documento corresponde ao critério fornecido.", "\033[0m")

    return redirect(url_for('index'))


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
    username = "Guest"  # Usuário padrão se ninguém estiver logado
    if current_user and current_user.is_authenticated:
        username = current_user.username

    projeto = projeto_collection.find_one({'_id': ObjectId(id_projeto)})
    tarefa = None
    if projeto:
        for item in projeto.get('itens', []):
            if str(item['_id']) == id_tarefa:
                tarefa = item
                break

    print("\033[91m", f"Exclusão da tarefa {tarefa['nome']} do projeto {projeto['nome']} pelo Usuário {username}", "\033[0m")
    try:
        projeto_collection.update_one(
            {'_id': ObjectId(id_projeto)},
            {'$pull': {'itens': {'_id': ObjectId(str(id_tarefa))}}}
        )
    except Exception as e:
        return str(e), 500
    return redirect(url_for('index'))


@app.route('/update_tarefa/<id_projeto>/<id_tarefa>', methods=['POST'])
def update_tarefa(id_projeto, id_tarefa):
    username = "Guest"  # Usuário padrão se ninguém estiver logado
    if current_user and current_user.is_authenticated:
        username = current_user.username

    # Recuperar informações do projeto e tarefa usando os IDs
    projeto = projeto_collection.find_one({'_id': ObjectId(id_projeto)})
    tarefa = None
    if projeto:
        for item in projeto.get('itens', []):
            if str(item['_id']) == id_tarefa:
                tarefa = item
                break

    if not projeto or not tarefa:
        return jsonify({"error": "Projeto ou tarefa não encontrados"}), 404

    print("\033[95m", "Projeto:", projeto['nome'], "- Tarefa:", tarefa['nome'], "- Usuário:", username, "\033[0m")

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


@app.route('/atualizar_aprovacao', methods=['POST'])
def atualizar_aprovacao():
    projeto_id = request.form.get('projeto_id')
    aprovado = request.form.get('aprovado') == 'true'

    # Atualize o banco de dados
    projeto_collection.update_one({'_id': ObjectId(projeto_id)}, {'$set': {'aprovado': aprovado}})

    return jsonify(success=True)


@app.route('/por_projetos', methods=['GET'])
def por_projetos():

    projetos = list(projeto_collection.find())
    projetos_pessoais = ['Artista Manoel Santos', 'Artista Micheal Jakson', 'Artista Janderson Nobre', 'Artista Rosa Santos']

    # Verificar se o usuário está logado
    if not current_user.is_authenticated:  # Substitua esta linha pelo seu método de verificação
        projetos = [proj for proj in projetos if proj['nome'] not in projetos_pessoais]

    # Ordenação manual em Python
    projetos.sort(key=lambda x: x['nome'].lower())

    edital_salvaguarda_coletivos = []
    edital_salvaguarda_metres = []
    edital_desenvolve_cultura_60 = []
    edital_desenvolve_cultura_30 = []
    edital_acoes_criativas = []
    edital_fomento_cultural = []
    nao_enviados = []

    for projeto in projetos:
        contem_edital = False
        for item in projeto.get('itens', []):
            nome_item = item.get('nome', '').lower()
            if 'edital' in nome_item:
                contem_edital = True
                if 'salvaguarda' in nome_item and 'coletivo' in nome_item:
                    edital_salvaguarda_coletivos.append(projeto)
                elif 'salvaguarda' in nome_item and 'mestr' in nome_item:
                    edital_salvaguarda_metres.append(projeto)
                elif 'desenvolve' in nome_item and '60' in nome_item:
                    edital_desenvolve_cultura_60.append(projeto)
                elif 'desenvolve' in nome_item and '30' in nome_item:
                    edital_desenvolve_cultura_30.append(projeto)
                elif 'criativas' in nome_item:
                    edital_acoes_criativas.append(projeto)
                elif 'fomento' in nome_item:
                    edital_fomento_cultural.append(projeto)
        if not contem_edital:
            nao_enviados.append(projeto)

    contexto = {
        'edital_salvaguarda_coletivos': edital_salvaguarda_coletivos,
        'edital_salvaguarda_metres': edital_salvaguarda_metres,
        'edital_desenvolve_cultura_60': edital_desenvolve_cultura_60,
        'edital_desenvolve_cultura_30': edital_desenvolve_cultura_30,
        'edital_acoes_criativas': edital_acoes_criativas,
        'edital_fomento_cultural': edital_fomento_cultural,
        'nao_enviados': nao_enviados,
    }
    print(len(edital_salvaguarda_coletivos), len(edital_salvaguarda_metres), len(edital_desenvolve_cultura_60),
          len(edital_desenvolve_cultura_30), len(edital_acoes_criativas), len(edital_fomento_cultural), len(nao_enviados))
    return render_template('listapg.html', contexto=contexto)


@app.route('/vincular', methods=['GET', 'POST'])
def vincular():
    if request.method == 'POST':
        projeto_id = request.form.get('projeto')
        link_mapa = request.form.get('link_mapa')

        result = projeto_collection.update_one(
            {'_id': ObjectId(projeto_id)},
            {'$set': {'mapa': link_mapa}}
        )

        if result.matched_count > 0:
            print("\033[92m", f"Documento atualizado com sucesso - {link_mapa}", "\033[0m")
        else:
            print("\033[92m", f"Nenhum documento corresponde ao critério fornecido  - {link_mapa}", "\033[0m")

        return redirect(url_for('vincular'))

    projetos = list(projeto_collection.find())
    return render_template('vincular.html', projetos=projetos)


@app.route('/adicionar_proponente', methods=['GET', 'POST'])
def adicionar_proponente():
    if request.method == 'POST':
        projeto_id = request.form.get('projeto_id')
        if projeto_id:
            nome_proponente = request.form.get('nome_proponente')
            rg = request.form.get('rg_proponente')
            emissor = request.form.get('emissor_proponente')
            cpf = request.form.get('cpf_proponente')
            sexo = request.form.get('sexo_proponente')
            estado_civil = request.form.get('estado_civil')
            rua = request.form.get('rua_proponente')
            numero = request.form.get('numero_proponente')
            bairro = request.form.get('bairro_proponente')
            cidade = request.form.get('cidade_proponente')
            cep = request.form.get('cep_proponente')

            proponente_data = {
                'nome_proponente': nome_proponente,
                'rg': rg,
                'emissor': emissor,
                'cpf': cpf,
                'sexo': sexo,
                'estado_civil': estado_civil,
                'rua': rua,
                'numero': numero,
                'bairro': bairro,
                'cidade': cidade,
                'cep': cep
            }

            # Verificar se um proponente já existe
            projeto_existente = projeto_collection.find_one({'_id': ObjectId(projeto_id), 'proponente': {'$exists': True}})

            if projeto_existente:
                # Se o proponente já existir, substitua os dados do proponente
                result = projeto_collection.update_one(
                    {'_id': ObjectId(projeto_id)},
                    {'$set': {'proponente': [proponente_data]}}
                )
            else:
                # Se o proponente ainda não existir, adicione um novo
                result = projeto_collection.update_one(
                    {'_id': ObjectId(projeto_id)},
                    {'$push': {'proponente': proponente_data}}
                )

            if result.matched_count > 0:
                print("\033[92m", "Proponente atualizado com sucesso!", "\033[0m")
            else:
                print("\033[91m", "Nenhum documento corresponde ao critério fornecido.", "\033[0m")

            return redirect(url_for('adicionar_proponente'))

    projetos = list(projeto_collection.find())
    projetos.sort(key=lambda x: x['nome'].lower())

    # Adicionar "Selecione o Projeto" como o primeiro item da lista
    placeholder_projeto = {
        '_id': None,
        'nome': 'Selecione o Projeto'
    }
    projetos.insert(0, placeholder_projeto)

    for projeto in projetos:
        if isinstance(projeto['_id'], ObjectId):
            projeto['_id'] = str(projeto['_id'])

    return render_template('adicionar_proponente.html', projetos=projetos)


@app.route('/paulogustavo', methods=['GET'])
def lista_paulo_gustavo():

    projetos = list(projeto_collection.find())
    projetos_pessoais = ['Artista Manoel Santos', 'Artista Micheal Jakson', 'Artista Janderson Nobre', 'Artista Rosa Santos']

    # Verificar se o usuário está logado
    if not current_user.is_authenticated:  # Substitua esta linha pelo seu método de verificação
        projetos = [proj for proj in projetos if proj['nome'] not in projetos_pessoais]
    #print("\033[95m", projetos[0])

    # Ordenação manual em Python
    projetos.sort(key=lambda x: x['nome'].lower())
    #print("\033[95m", projetos[0])
    return render_template('listapg.html', projetos=projetos)


@app.route('/lista_mapas', methods=['GET'])
def lista_mapas():

    projetos = list(projeto_collection.find())
    projetos_pessoais = ['Artista Manoel Santos', 'Artista Micheal Jakson', 'Artista Janderson Nobre', 'Artista Rosa Santos']

    # Verificar se o usuário está logado
    if not current_user.is_authenticated:  # Substitua esta linha pelo seu método de verificação
        projetos = [proj for proj in projetos if proj['nome'] not in projetos_pessoais]

    # Separar projetos que têm 'cidade' e os que não têm
    projetos_com_cidade = [proj for proj in projetos if 'cidade' in proj and proj['cidade']]
    projetos_sem_cidade = [proj for proj in projetos if 'cidade' not in proj or not proj['cidade']]

    # Ordenar projetos que têm 'cidade' pelo nome da cidade
    projetos_com_cidade = sorted(projetos_com_cidade, key=lambda x: x['cidade'].lower())

    # Combinar as duas listas: projetos com 'cidade' seguidos por projetos sem 'cidade'
    projetos = projetos_com_cidade + projetos_sem_cidade

    #print("\033[95m", projetos[0])
    return render_template('lista_mapas.html', projetos=projetos)


@app.route('/export_to_excel')
def export_to_excel():
    # Obter projetos de sua fonte de dados, tal como um banco de dados
    # Neste exemplo, estou usando uma lista de dicionários para simulação
    projetos = list(projeto_collection.find())

    # Criar lista para armazenar os dados
    data = []

    for projeto in projetos:
        for item in projeto.get('itens', []):
            row = {
                'Projeto': projeto['nome'],
                'Tarefa': item['nome'],
                'Status Tarefa': 'Feito' if item['feito'] else 'Não Feito',
                'Data Criado': projeto['data_criado'],
                'Mapa': projeto.get('mapa', ''),
                'Foto Perfil': projeto.get('foto_perfil', ''),
                'Nome no Mapa': projeto.get('nome_mapa', '')
            }
            data.append(row)

    # Criar DataFrame
    df = pd.DataFrame(data)

    # Exportar para Excel e salvar temporariamente
    filename = 'backup_projetos.xlsx'
    df.to_excel(filename, index=False)

    return send_file(filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True,
                     download_name='backup_projetos.xlsx')


@app.route('/download_pdf/')
def download_pdf():
    project_name = request.args.get('project_name')
    print(project_name)
    projeto = projeto_collection.find_one({'nome': project_name})

    if projeto is None:
        return "Projeto não encontrado", 404  # HTTP 404 Not Found

    # Renderizar um template HTML com os dados do projeto
    rendered = render_template('pdf_template.html', projeto=projeto)

    options = {
        'no-images': '',
        'encoding': 'utf-8',
    }

    # Criar o PDF usando pdfkit e wkhtmltopdf
    config = pdfkit.configuration(wkhtmltopdf='/usr/bin/wkhtmltopdf')  # atualize este caminho
    pdf = pdfkit.from_string(rendered, False, configuration=config)

    # Salvar o PDF em um arquivo temporário e enviar como resposta
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=True) as f:
        f.write(pdf)
        f.flush()
        return send_file(f.name, attachment_filename=f"{project_name}.pdf", as_attachment=True)


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