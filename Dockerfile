# Utiliza una imagen de Python ligera
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia primero el archivo de requirements y lo instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo el contenido del proyecto al contenedor
COPY . .

# Comando para correr la aplicación
CMD ["uvicorn", "application:app", "--host", "0.0.0.0", "--port", "80"]
