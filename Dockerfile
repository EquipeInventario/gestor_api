FROM python:3.11-slim

# Instala dependências básicas
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unixodbc \
    unixodbc-dev \
    apt-transport-https \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Adiciona chave Microsoft (forma nova)
RUN mkdir -p /etc/apt/keyrings && \
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg

# Adiciona repositório Microsoft
RUN echo "deb [signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# Instala driver SQL Server
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# App
WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
