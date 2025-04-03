import os
import json
import boto3
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Cargar variables de entorno desde .env (para desarrollo local)
load_dotenv()

def get_secret_key() -> str:
    # Primero intenta cargar desde AWS Secrets Manager (producción)
    try:
        secret_name = os.getenv("SECRET_NAME", "fastapi-secret-key")  # Nombre del secreto en AWS Secrets Manager
        region_name = os.getenv("AWS_REGION", "us-east-1")  # Región de AWS (ajustar según corresponda)

        # Crear el cliente de boto3 para acceder a Secrets Manager
        client = boto3.client("secretsmanager", region_name=region_name)
        
        # Recuperar el secreto
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response["SecretString"])  # Decodificar el secreto en JSON

        return secret["SECRET_KEY"]  # Devolver la clave secreta
    except ClientError as e:
        print(f"[INFO] No se pudo obtener el secreto desde Secrets Manager. Usando .env. ({e})")
    except Exception as e:
        print(f"[ERROR] Falla inesperada con Secrets Manager: {e}")

    # Si no está en Secrets Manager, buscar en .env (desarrollo local)
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise RuntimeError("SECRET_KEY no está definido ni en Secrets Manager ni en .env")
    
    return secret_key

# Usado en el resto de la aplicación
SECRET_KEY = get_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Configuración de la base de datos (si la usas en tu proyecto)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cleaning:admin@localhost/cleaning")
