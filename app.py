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

notas_mapeamento = {}  # Mapeia o título da nota para o ID do arquivo do Box
id_mapeamento = {}  # Mapeia o ID interno para o título e o ID do arquivo do Box

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

# Função para deletar arquivo no Box usando apenas o ID
def deletar_arquivo_box(client, file_id):
    try:
        # Deleta o arquivo no Box usando o file_id
        client.file(file_id).delete()

        # Retorna uma resposta de sucesso
        resposta = {"status": "deleted","id": file_id}

    except Exception as e:
        print(f"Erro ao deletar o arquivo: {str(e)}")
        raise

    return resposta

# Função para sincronizar o mapeamento com o Box
def sincronizar_mapeamento():
    client = criar_cliente_box()
    folder = client.folder('0')
    items = folder.get_items(limit=1000)

    novo_mapeamento = {}
    novo_id_mapeamento = {}
    id_counter = 1  # Contador para IDs internos

    for item in items:
        if item.type == 'file':
            titulo = item.name.rsplit('.', 1)[0]  # Remove a extensão do nome do arquivo
            file_id = item.id
            novo_mapeamento[titulo] = file_id
            novo_id_mapeamento[id_counter] = {"titulo": titulo, "file_id": file_id}
            id_counter += 1

    global notas_mapeamento, id_mapeamento
    notas_mapeamento = novo_mapeamento
    id_mapeamento = novo_id_mapeamento
    print(f"Mapeamento sincronizado com sucesso: {notas_mapeamento}")
    print(f"ID Mapeamento sincronizado com sucesso: {id_mapeamento}")

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

# Método DELETE
@app.route('/', methods=['DELETE'])
def deletar_nota():
    dados = request.json
    nota_id = dados.get('id')  # Recebe o ID interno da nota

    print(f"Dados recebidos para deletar: {dados}")

    if not nota_id:
        print("Erro: ID da nota não fornecido.")
        return jsonify({"error": "ID da nota não fornecido."}), 400

    # Sincroniza o mapeamento antes de tentar deletar o arquivo
    sincronizar_mapeamento()

    # Use o ID interno para encontrar o ID do arquivo no mapeamento
    nota_info = id_mapeamento.get(nota_id)
    if not nota_info:
        print("Erro: Arquivo não encontrado no mapeamento para o ID fornecido.")
        return jsonify({"error": "Arquivo não encontrado no mapeamento para o ID fornecido."}), 404

    titulo = nota_info["titulo"]
    file_id = nota_info["file_id"]

    try:
        print("Criando o cliente Box...")
        client = criar_cliente_box()

        print(f"Tentando deletar o arquivo no Box com File ID: {file_id}...")
        resposta = deletar_arquivo_box(client, file_id)
        print(f"Arquivo deletado no Box com sucesso. Resposta: {resposta}")

        # Remove a entrada do mapeamento
        del notas_mapeamento[titulo]
        del id_mapeamento[nota_id]
        print(f"Nota removida do mapeamento local. Título: {titulo}")

        return jsonify({"message": "Arquivo deletado com sucesso no Box."}), 200

    except Exception as e:
        print(f"Erro ao deletar nota: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)