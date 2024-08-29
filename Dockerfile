# Imagem base do Python
FROM python:3.9-slim

# Diretório de trabalho dentro do contêiner
WORKDIR /app

# Arquivo requirements.txt e app.py para o diretório de trabalho
COPY .env /app/
COPY requirements.txt .
COPY app.py .

# Dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Porta 5000
EXPOSE 5002

# Variável de ambiente
ENV FLASK_APP=app.py

# Comando para rodar a aplicação
CMD ["flask", "run", "--host=0.0.0.0", "--port=5002"]
