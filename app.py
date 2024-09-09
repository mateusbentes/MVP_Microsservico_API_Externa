from flask import Flask, request, jsonify
from boxsdk import OAuth2, Client
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os
import io
import tempfile

app = Flask(__name__)

# CORS adicona o método POST e PUT
CORS(app)

# Carrega variáveis do ambiente
load_dotenv()

# Mapeamento de notas para seus IDs no Box (simulação de armazenamento local)
notas_mapeamento = {}

# Função para obter o access token e refresh token
def obter_tokens():
    url = "https://api.box.com/oauth2/token"
    client_id = os.getenv('BOX_CLIENT_ID')
    client_secret = os.getenv('BOX_CLIENT_SECRET')
    refresh_token = os.getenv('BOX_REFRESH_TOKEN')  # Código de autorização que é obtido
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': client_id,
        'client_secret': client_secret
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}  

    try:
        resposta = requests.post(url, data=data, headers=headers)
        resposta.raise_for_status()  # Levanta uma exceção para códigos de status não 200
        resposta_json = resposta.json()

        access_token = resposta_json.get('access_token')
        novo_refresh_token = resposta_json.get('refresh_token')

        if not access_token:
            raise Exception("Failed to retrieve access token: {}".format(resposta_json))

        # Atualiza o refresh token no ambiente ou em um armazenamento seguro
        os.environ['BOX_REFRESH_TOKEN'] = novo_refresh_token

        return access_token, novo_refresh_token

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving tokens: {e}")
        raise

def criar_cliente_box():
    access_token, refresh_token = obter_tokens()
    oauth = OAuth2(
        client_id=os.getenv('BOX_CLIENT_ID'),
        client_secret=os.getenv('BOX_CLIENT_SECRET'),
        access_token=access_token,
        refresh_token=refresh_token
    )

    return Client(oauth)

# Função para adicionar o ID do arquivo ao mapeamento
def adicionar_ao_mapeamento(titulo, file_id):
    notas_mapeamento[titulo] = file_id

# Função para criar arquivo no Box e adicionar ao mapeamento
def criar_arquivo_box(client, titulo, texto):
    arquivo_raiz = client.folder('0')
    nome_arquivo = f"{titulo}.txt"
    file_stream = io.BytesIO(texto.encode('utf-8'))
    arquivo = arquivo_raiz.upload_stream(file_stream, nome_arquivo)

    # Adiciona o ID ao mapeamento
    adicionar_ao_mapeamento(titulo, arquivo.id)

    return {"id": arquivo.id, "name": arquivo.name, "size": arquivo.size}

# Função para atualizar arquivo no Box
def atualizar_arquivo_box(client, file_id, novo_texto):
    # Verificação para garantir que o file_id está presente
    if not file_id:
        raise ValueError("File ID is missing.")

    # Cria um arquivo temporário para o novo conteúdo
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(novo_texto.encode('utf-8'))
        temp_file_path = temp_file.name

    try:
        # Atualiza o conteúdo do arquivo usando o caminho temporário
        file = client.file(file_id).update_contents(temp_file_path)

        # Obtém o 'id' corretamente a partir do dicionário _response_object
        file_response = file._response_object.get('entries', [])[0]  # Obtém o primeiro item da lista 'entries'
        if not file_response or 'id' not in file_response:
            raise Exception("A resposta do Box não contém o 'id' do arquivo.")

        # Extrai o 'id' do dicionário correto
        resposta = {"id": file_response['id'], "name": file_response['name'], "size": file_response['size']}

    except Exception as e:
        print(f"Erro ao atualizar o arquivo: {str(e)}")
        raise

    finally:
        # Remove o arquivo temporário após a atualização
        os.remove(temp_file_path)

    return resposta

# Método POST
@app.route('/', methods=['POST'])
def adicionar_nota():
    dados = request.json
    titulo = dados.get('titulo')
    texto = dados.get('texto')
    
    if not titulo or not texto:
        return jsonify({"error": "Faltando título ou texto"}), 400
    
    try:
        client = criar_cliente_box()
        resposta = criar_arquivo_box(client, titulo, texto)

        # Armazena o ID da nota junto com o título
        notas_mapeamento[titulo] = resposta['id']

        return jsonify(resposta), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Método PUT
@app.route('/', methods=['PUT'])
def atualizar_nota():
    dados = request.json
    titulo = dados.get('titulo')
    novo_texto = dados.get('texto')
    file_id = dados.get('file_id')  # Adiciona suporte para o file_id diretamente

    if not novo_texto:
        return jsonify({"error": "Faltando texto"}), 400

    if not file_id:  # Caso o file_id não seja fornecido, tenta obter pelo título
        if not titulo:
            return jsonify({"error": "Faltando título ou file_id"}), 400
        file_id = notas_mapeamento.get(titulo)
        if not file_id:
            return jsonify({"error": "Arquivo não encontrado para o título fornecido"}), 404

    try:
        client = criar_cliente_box()

        # Atualiza o conteúdo do arquivo
        resposta = atualizar_arquivo_box(client, file_id, novo_texto)
        return jsonify(resposta), 200

    except Exception as e:
        print(f"Erro ao atualizar nota: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)