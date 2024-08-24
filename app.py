from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests
import os

app = Flask(__name__)

CORS(app)

load_dotenv()  # Carrega as variáveis do arquivo .env

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DATABASE_ID = os.getenv("DATABASE_ID")

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

url = f"https://api.notion.com/v1/databases/{DATABASE_ID}"

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.json())

def criar_pagina(titulo, conteudo):
    create_url = "https://api.notion.com/v1/pages"

    payload = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": titulo
                        }
                    }
                ]
            }
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": conteudo
                            }
                        }
                    ]
                }
            }
        ]
    }

    resposta = requests.post(create_url, headers=headers, json=payload)

    print("Status Code:", resposta.status_code)
    print("Response Content:", resposta.content)
    
    return resposta.json()

@app.route('/', methods=['POST'])
def adicionar_nota():
    dados = request.json
    titulo = dados.get('titulo')
    conteudo = dados.get('conteudo')
    
    if not titulo or not conteudo:
        return jsonify({"error": "Faltando título ou conteúdo"}), 400
    
    resposta = criar_pagina(titulo, conteudo)
    return jsonify(resposta)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=5002)