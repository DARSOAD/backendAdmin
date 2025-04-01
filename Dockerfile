# Imagen base de Python
FROM python:3.11-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar archivos de requerimientos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto de la app
COPY . .

# Exponer el puerto que App Runner espera
EXPOSE 8080

# Comando de arranque
CMD ["uvicorn", "application:app", "--host", "0.0.0.0", "--port", "8080"]
