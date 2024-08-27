# Meu Back-End

Back-end do MVP **Bloco de Notas** (Microsserviço da API Externa)

---
## Como executar

Após clonar o repositório, é necessário ir ao diretório raiz, pelo terminal, para poder executar os comandos descritos abaixo.

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
$ docker build -t microsservico-Box  .
```

Uma vez criada a imagem, para executar o container basta executar, **como administrador**, seguinte o comando:

```
$ docker run --network="host" microsservico-Box
```
