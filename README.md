# Meu Back-End

Back-end do MVP **Bloco de Notas** (Microsserviço da API Externa)

---
## Passos iniciais

> É necessário ter uma conta no Box junto com uma conta no Box Developer Console [Box Developer Console](https://app.box.com/developers/console).

> É necessário a criação de uma nova aplicação com autenticação oAuth 2.0 e dentro da aplicação em Configuration é necessário criar um link em OAuth 2.0 Redirect URIs da seguinte maneira http://localhost/callback

Após clonar o repositório, é necessário ir ao diretório raiz e criar um arquivo .env com a seguinte estrutura:

```
BOX_CLIENT_ID=Meu_Client_Id
BOX_CLIENT_SECRET=Meu_Client_Secret
BOX_REFRESH_TOKEN=Meu_Refresh_Token
```

> O Meu_Client_Id e o Meu_Client_Secret podem ser adiquiridos em OAuth 2.0 Credentials.

> Para adiquirir o Meu_Refresh_Token é necessário seguir os passos abaixo.

Em um navegador é necessário digitar a seguinte URL substituindo Meu_Client_Id respectivamente:

```
https://account.box.com/api/oauth2/authorize?response_type=code&client_id=Meu_Client_Id&redirect_uri=http://localhost/callback
```
É necessário clicar em Grant acess to Box e o resultado será algo tipo:

```
http://localhost/callback?code=Meu_Acess_Token
```

Depois disso no terminal é necessário digitar o seguinte comando substituindo Meu_Client_Id, Meu_Client_Secret e Meu_Acess_Token respectivamente:

```
curl -i -X POST "https://api.box.com/oauth2/token" \
-H "content-type: application/x-www-form-urlencoded" \
-d "grant_type=authorization_code" \
-d "code=Meu_Acess_Token" \
-d "client_id=Meu_Client_Id" \
-d "client_secret=Meu_Client_Secret" \
-d "redirect_uri=http://localhost/callback"
```

O resultado será algo do tipo:

```
HTTP/2 200
date: Thu, 29 Aug 2024 11:34:57 GMT
content-type: application/json
content-length: 193
strict-transport-security: max-age=31536000
set-cookie: box_visitor_id=66d05ce1377e09.30785707; expires=Fri, 29-Aug-2025 11:34:57 GMT; Max-Age=31536000; path=/; domain=.box.com; secure; SameSite=None
set-cookie: bv=SECENGG-3134; expires=Thu, 05-Sep-2024 11:34:57 GMT; Max-Age=604800; path=/; domain=.app.box.com; secure
set-cookie: cn=59; expires=Fri, 29-Aug-2025 11:34:57 GMT; Max-Age=31536000; path=/; domain=.app.box.com; secure
set-cookie: site_preference=desktop; path=/; domain=.box.com; secure
cache-control: no-store
via: 1.1 google
alt-svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000

{"access_token":"Meu_Acess_Token","expires_in":4140,"restricted_to":[],"refresh_token":"Meu_Refresh_Token","token_type":"bearer"}
```

O Meu_Client_Id, o Meu_Client_Secret e o Meu_Refresh_Token devem ser substituidos no arquivo .env respectivamente.

---
## Como executar

É necessário ir ao diretório raiz, pelo terminal, para poder executar os comandos descritos abaixo.

> É fortemente indicado o uso de ambientes virtuais do tipo [virtualenv](https://virtualenv.pypa.io/en/latest/installation.html).


Será necessário a criação doo diretório do virtual enviroment, o myvenv.

```
$ mkdir myvenv
```

Será criado o virtual enviroment propriamente, através do comando:

```
$ virtualenv myvenv
```

Para utilização do virtual enviroment ele deverá ser acessado com o comando abaixo:

```
$ source myvenv/bin/activate
```

Será necessário ter todas as libs python listadas no `requirements.txt` instaladas.

```
(myenv)$ pip install -r requirements.txt
```

Este comando instala as dependências/bibliotecas, descritas no arquivo `requirements.txt`.

Para executar a API  basta executar:

```
(myenv)$ flask run --host 0.0.0.0 --port 5002
```

Em modo de desenvolvimento é recomendado executar utilizando o parâmetro reload, que reiniciará o servidor automaticamente após uma mudança no código fonte. 

```
(myenv)$ flask run --host 0.0.0.0 --port 5002 --reload
```

---
## Como executar através do Docker

Certifique-se de ter o [Docker](https://docs.docker.com/engine/install/) instalado e em execução em sua máquina.

Navegue até o diretório que contém o Dockerfile e o requirements.txt no terminal.
Execute **como administrador** o seguinte comando para construir a imagem Docker:

```
$ docker build -t microsservico-box  .
```

Uma vez criada a imagem, para executar o container basta executar, **como administrador**, seguinte o comando:

```
$ docker run --network="host" microsservico-box
```
