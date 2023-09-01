import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from mongo_connection import get_mongo_client

# Conexão com o MongoDB
client = get_mongo_client()
db = client['MeuChecklist']

projeto_collection = db['projetos']

# Buscar projetos com atributo 'mapa'
projetos = projeto_collection.find({'mapa': {'$exists': True, '$ne': None}})

for projeto in projetos:
    if projeto['mapa']:
        print("\033[93m", f"Encontrado link para Projeto {projeto['nome']}")
        url = projeto['mapa']
        print(url)
        # Fazer uma requisição HTTP para obter o conteúdo da página
        response = requests.get(url)

        if response.status_code == 200:
            # Fazer o parsing do HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            #print('soup', soup)
            # Encontrar o elemento com a classe 'avatar'
            avatar_div = soup.find('div', class_='avatar')

            if avatar_div:
                # Extrair o URL da imagem
                img_tag = avatar_div.find('img', class_='js-avatar-img')
                if img_tag:
                    img_url = img_tag['src']

                    # Atualizar o atributo 'foto_perfil' no MongoDB
                    projeto_collection.update_one(
                        {'_id': projeto['_id']},
                        {'$set': {'foto_perfil': img_url}}
                    )
                    print("\033[92m", f"Foto de perfil atualizada para o projeto {projeto['nome']}")
                else:
                    print("\033[91m", f"Nenhum elemento de imagem encontrado para o projeto {projeto['nome']}")
            else:
                print("\033[91m", f"Nenhum avatar encontrado para o projeto {projeto['nome']}")

            # Encontrar o elemento com a classe 'js-editable' para o nome
            nome_span = soup.find('span', class_='js-editable')
            if nome_span:
                nome_mapa = nome_span.text

                # Atualizar o atributo 'nome_mapa' no MongoDB
                projeto_collection.update_one(
                    {'_id': projeto['_id']},
                    {'$set': {'nome_mapa': nome_mapa}}
                )
                print("\033[92m", f"Nome do Mapa Cultural atualizado para o projeto {projeto['nome']}")
            else:
                print("\033[91m", f"Nenhum nome encontrado no Mapa Cultural para o projeto {projeto['nome']}")

        else:
            print("\033[91m", f"Não foi possível acessar a URL {url} para o projeto {projeto['nome']}")

