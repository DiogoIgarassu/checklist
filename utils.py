from datetime import datetime
from app import db
from models import User
from bson.objectid import ObjectId

projeto_collection = db['projetos']
user_collection = db['usuarios']  # Adicionei esta linha para a coleção de usuários

artistas_e_trupes = [
    "Artista Alexsandra Basilio",
    "Artista Barbara Finsking",
    "Artista Cida Show",
    "Artista Daniely Bianca",
    "Artista Danilo Silva",
    "Artista Diana Show",
    "Artista Diogo Albuquerque",
    "Artista Gilvania Medeiros",
    "Artista Jair Alves",
    "Artista Manoel Santos",
    "Artista Micheal Jakson",
    "Artista Palhaço Cascudinho",
    "Artista Palhaça Kassia",
    "Artista Palhaça Malandrinha",
    "Artista Sandro Alves",
    "Artista Victor Santos",
    "Circo do Palhaço Cascudinho",
    "Circo do Palhaço Gostosinho",
    "Circo do Palhaço Latinha",
    "Circo Lorrane",
    "Circo Pimentinha",
    "Circo Raio do Sol",
    "Circo Rayane",
    "Trupe Chupeta e Paçoquinha",
    "Trupe do Palhaço Birrinho",
    "Trupe Família Ribeiro",
    "Trupe Geleia e Gelatina",
    "Trupe Irmãos Dantas",
    "Trupe Irmãos Lisboas",
    "Trupe Irmãos Michaels",
    "Trupe Pipoca e Pipoquinha",
    "Trupe The Flying Lisboa"
]

tarefas = [
    "RG",
    "CPF",
    "Comprovante de Residência Atual",
    "Comprovações Artísticas",
    "Currículo Artístico",
    "Histórico Atualizado (Ano de Início)",
    "Cadastro Mapa Cultural",
    "Número Telefone",
    "Cor",
    "Gênero",
    "Grau de Escolaridade",
    "Recebe algum benefício do governo?",
    "Recebeu recursos públicos últimos 5 anos?"
]

from bson import ObjectId


def criar_tarefas_gerais(lista_tarefas=None, projetos_nomes=None):
    resposta = input("Tem certeza de que deseja continuar? Isso pode resultar em perda de informações. (Sim/Não): ").strip().lower()

    if resposta != 'sim':
        print("\033[93m", "Operação cancelada pelo usuário.", "\033[0m")
        return

    if not lista_tarefas:
        lista_tarefas = tarefas  # assumindo que 'tarefas' é uma variável global

    # Filtrar projetos com base na lista fornecida de nomes de projetos
    projetos_nomes = ['Artista Rosa Santos']

    # Montar a query para encontrar os projetos desejados
    query = {}
    if projetos_nomes:
        query['nome'] = {'$in': projetos_nomes}

    todos_projetos = projeto_collection.find(query)

    for projeto in todos_projetos:
        id_projeto = projeto['_id']
        tarefas_existentes = {item['nome'] for item in projeto.get('itens', [])}  # Usando get() para evitar KeyError

        for nome_tarefa in lista_tarefas:
            if nome_tarefa not in tarefas_existentes:
                novo_id = ObjectId()
                print("\033[93m", f"Criando tarefa {nome_tarefa} para {projeto['nome']}", "\033[0m")
                projeto_collection.update_one(
                    {'_id': ObjectId(id_projeto)},
                    {'$push': {'itens': {'_id': novo_id, 'nome': nome_tarefa, 'feito': False}}}
                )


def criar_projetos_gerais(lista_projetos=None):
    if not lista_projetos:
        lista_projetos = artistas_e_trupes

    projetos_existentes = {projeto['nome'] for projeto in projeto_collection.find()}

    now = datetime.now()
    formatted_date = now.strftime("%d/%m/%Y às %H:%M")

    for nome_projeto in lista_projetos:
        if nome_projeto not in projetos_existentes:
            print("\033[93m", f'Criando projeto {nome_projeto} ...', "\033[0m")
            projeto_collection.insert_one({
                'nome': nome_projeto,
                'itens': [],
                'status': 'Em Andamento',
                'data_criado': formatted_date
            })


def listar_projetos(nomes_projetos=None):
    if nomes_projetos is None:
        # Se nenhum nome de projeto foi passado como argumento, buscar todos os projetos
        projetos = list(projeto_collection.find())
    else:
        # Se uma lista de nomes de projetos foi passada como argumento, buscar esses projetos específicos
        projetos = list(projeto_collection.find({'nome': {'$in': nomes_projetos}}))

    try:
        if nomes_projetos:
            for projeto in projetos:
                print("\033[94m", f"{projeto}", "\033[0m")
        else:
            # Ordenação manual em Python
            projetos.sort(key=lambda x: x['nome'].lower())
            for projeto in projetos:
                print("\033[94m", f"{projeto['nome']}", "\033[0m")
    except Exception as e:
        return print(str(e))


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


def excluir_todas_tarefas():
    try:
        projeto_collection.update_many(
            {},  # Uma query vazia seleciona todos os documentos
            {'$set': {'itens': []}}  # Define o campo 'itens' como uma lista vazia
        )
    except Exception as e:
        return str(e), 500
    return print("\033[91m", f"Todas as tarefas apagadas com sucesso!", "\033[0m")


def listar_projetos_e_proponentes():
    # Buscar todos os projetos
    projetos = list(projeto_collection.find())

    try:
        # Ordenar os projetos pelo nome
        projetos.sort(key=lambda x: x['nome'].lower())

        for projeto in projetos:
            # Imprimir o nome do projeto
            print("\033[94m", f"Nome do Projeto: {projeto['nome']}", "\033[0m")

            # Acessar o campo 'proponente' no projeto, se existir
            proponente_data = projeto.get('proponente')

            if proponente_data is not None:
                if isinstance(proponente_data, list):  # Caso seja uma lista de dicionários
                    for i, proponente in enumerate(proponente_data):
                        print(f"  Proponente {i + 1}:")
                        print_proponente_info(proponente)
                elif isinstance(proponente_data, dict):  # Caso seja um único dicionário
                    print("  Proponente:")
                    print_proponente_info(proponente_data)
                else:
                    print("  Tipo de dados do proponente não suportado.")
            else:
                print("  Sem proponentes.")

    except Exception as e:
        print(str(e))


def print_proponente_info(proponente):
    print(f"    Nome: {proponente.get('nome_proponente', 'N/A')}")
    print(f"    RG: {proponente.get('rg', 'N/A')} ({proponente.get('emissor', 'N/A')})")
    print(f"    CPF: {proponente.get('cpf', 'N/A')}")
    print(f"    Sexo: {proponente.get('sexo', 'N/A')}")
    print(f"    Estado Civil: {proponente.get('estado_civil', 'N/A')}")
    print(f"    Endereço: Rua {proponente.get('rua', 'N/A')}, Nº {proponente.get('numero', 'N/A')}")
    print(f"    Bairro: {proponente.get('bairro', 'N/A')}, Cidade: {proponente.get('cidade', 'N/A')}")
    print(f"    CEP: {proponente.get('cep', 'N/A')}")


def delete_proponente_by_project_name(project_name):
    projeto = projeto_collection.find_one({'nome': project_name})

    # Verificar se o projeto foi encontrado
    if projeto:
        # Deletar o campo "proponente"
        projeto_collection.update_one({'_id': projeto['_id']}, {'$unset': {'proponente': ""}})
        print(f"Campo 'proponente' do projeto {project_name} foi removido com sucesso.")
    else:
        print(f"Projeto com nome {project_name} não encontrado.")


def substituir_nome_projeto(nome_antigo, nome_novo):
    """
    Substitui o nome antigo do projeto pelo nome novo na coleção de projetos.

    Args:
    - nome_antigo (str): Nome antigo do projeto.
    - nome_novo (str): Nome novo para o projeto.

    Returns:
    - str: Mensagem indicando sucesso ou falha na operação.
    """

    # Verificar se o projeto com o nome antigo existe
    projeto = projeto_collection.find_one({'nome': nome_antigo})

    if not projeto:
        return f"Projeto com nome '{nome_antigo}' não encontrado."

    # Atualizar o nome do projeto
    projeto_collection.update_one({'_id': projeto['_id']}, {'$set': {'nome': nome_novo}})

    return f"Nome do projeto atualizado de '{nome_antigo}' para '{nome_novo}' com sucesso."

# Testando a função
# nome_antigo = input("Digite o nome antigo do projeto: ")
# nome_novo = input("Digite o novo nome para o projeto: ")