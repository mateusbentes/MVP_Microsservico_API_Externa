from flask import Flask, request, jsonify
from boxsdk import OAuth2, Client
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os
import io

app = Flask(__name__)

# CORS adicona o método POST
CORS(app)

# Carrega variáveis do ambiente
load_dotenv()

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
        raise  # Re-raise a exceção para ser capturada pela função chamador

# Função para criar o cliente Box autenticado
def criar_cliente_box():
    access_token, refresh_token = obter_tokens()
    oauth = OAuth2(
        client_id=os.getenv('BOX_CLIENT_ID'),
        client_secret=os.getenv('BOX_CLIENT_SECRET'),
        access_token=access_token,
        refresh_token=refresh_token
    )

    return Client(oauth)

# Função para criar arquivo no Box
def criar_arquivo_box(client, titulo, texto):
    arquivo_raiz = client.folder('0')  # '0' refere-se à raiz da conta do Box

    nome_arquivo = f"{titulo}.txt"
    file_stream = io.BytesIO(texto.encode('utf-8'))
    arquivo = arquivo_raiz.upload_stream(file_stream, nome_arquivo)

    return {"id": arquivo.id, "name": arquivo.name, "size": arquivo.size}

# Médoto POST
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
        return jsonify(resposta), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)