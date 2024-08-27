from flask import Flask, request, jsonify
from boxsdk import OAuth2, Client
from boxsdk.exception import BoxAPIException
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os
import io

app = Flask(__name__)

CORS(app)

# Carrega variáveis do ambiente
load_dotenv()

# Configuração OAuth2
oauth = OAuth2(
    client_id=os.getenv('BOX_CLIENT_ID'),
    client_secret=os.getenv('BOX_CLIENT_SECRET'),
    access_token=os.getenv('BOX_ACCESS_TOKEN')
)

# Cria o cliente do Box
client = Client(oauth)

def criar_arquivo_box(client, titulo, conteudo):
    arquivo_raiz = client.folder('0')  # '0' refere-se à raiz da conta do Box

    nome_arquivo = f"{titulo}.txt"
    file_stream = io.BytesIO(conteudo.encode('utf-8'))

    # O método upload_stream() recebe o nome do arquivo como primeiro argumento e o stream de dados como segundo
    arquivo = arquivo_raiz.upload_stream(nome_arquivo, file_stream)

    return arquivo

@app.route('/', methods=['POST'])
def adicionar_nota():
    dados = request.json
    titulo = dados.get('titulo')
    conteudo = dados.get('conteudo')
    
    if not titulo or not conteudo:
        return jsonify({"error": "Faltando título ou conteúdo"}), 400
    
    resposta = criar_arquivo_box(client, titulo, conteudo)
    return jsonify(resposta)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5002)