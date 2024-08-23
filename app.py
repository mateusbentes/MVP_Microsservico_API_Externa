from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)

CORS(app)

# Chave de integração da API do Notion (substitua pela sua)
NOTION_TOKEN = "secret_9IyHhmCo1ajj8h6m3npJCZku57uKDrAgEv0pp0AbU02"
# ID do banco de dados onde as notas serão salvas
DATABASE_ID = "2f9e434650334cb480c5757b26dd0608"

headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

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
                    "text": [
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